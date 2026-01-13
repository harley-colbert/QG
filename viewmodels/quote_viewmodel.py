import logging
from typing import Any, Callable, Dict, List, Optional
from datetime import datetime

from config.config_manager import ConfigManager
from config.settings import Settings
from models.quote_model import QuoteModel, Quote
from services.database_manager import DatabaseManager
from services.sync_service import SyncService
from services.word import WordSubmissionHandler

from services.spell_checker import SpellCheckerService
from services.pmcalc import ProjectMilestonesCalculator
from utilities.util import merge_nested_dict
from pathlib import Path     

from models.headers import (
    header_data,
    key_data,
    budgetary_categories,
    final_categories,
    all_categories_order,
    optional_categories,
    incoterms_list,
    weeks_after_po_options,
    categories_with_add_button,
    spellcheck_categories,
    file_browse_fields
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

class QuoteViewModel:
    """
    ViewModel for the Quote Generator application.

    Exposes:
      - CRUD for quotes
      - Rich‑text fields (set_field/get_field)
      - OEE, milestone, and spell‑check logic
      - Alliance contacts & settings CRUD
      - Word‑template submission
      - Category metadata for dynamic rendering
    """

    def __init__(
        self,
        model: QuoteModel,
        db_manager: DatabaseManager,
        sync_service: SyncService,
    ) -> None:
        self.model        = model
        self.db_manager   = db_manager
        self.sync_service = sync_service
        self.config_manager = ConfigManager()
        self.logger       = logging.getLogger(self.__class__.__name__)
        self._last_flat_map: Dict[str,str] = {}

        # ────────────────────────────────────────────────────────────
        # Ensure there is exactly one Quote instance for all data
        # ────────────────────────────────────────────────────────────
        if not self.model.quotes:
            # no quotes yet → create one
            q = Quote(id=1, text="", author="")
            self.model.quotes[1] = q
        else:
            # grab the existing one (ignore any others)
            _, q = next(iter(self.model.quotes.items()))
        self.quote = q

        # this still drives which categories you *show* in the UI,
        # but it does NOT swap out self.quote
        self.quote_type = "final"
        

    # -------------------------
    # Category metadata endpoints
    # -------------------------
    def get_file_browse_fields(self) -> dict:
        # Return the file browse fields mapping from the headers module.
        return file_browse_fields

    

    
    def get_categories(self, quote_type: str) -> List[str]:
        qt = quote_type.strip().lower()
        if qt == "budgetary":
            cats = set(budgetary_categories)
        elif qt == "final":
            cats = set(final_categories)
        else:
            cats = set()
        return [c for c in all_categories_order if c in cats]

    def get_category_fields(self, category: str) -> List[Dict[str, Any]]:
        labels = header_data.get(category, [])
        keys = key_data.get(category, [])
        fields = []
        is_optional = category in optional_categories
        for label, key in zip(labels, keys):
            fields.append({
                "label": label,
                "key": key,
                "optional": is_optional
            })
        return fields

    def category_can_add(self, category: str) -> bool:
        return category in categories_with_add_button

    def get_special_lists(self) -> Dict[str, List[str]]:
        return {
            "incoterms": incoterms_list,
            "weeks_after_po": weeks_after_po_options
        }

    # -------------------------
    # Quote CRUD
    # -------------------------
    def get_quotes(self) -> Dict[int, Dict[str, Any]]:
        try:
            return {
                qid: {
                    "text": quote.text,
                    "author": quote.author,
                    "created_at": quote.created_at.isoformat(),
                    "data": quote.data,
                }
                for qid, quote in self.model.quotes.items()
            }
        except Exception:
            self.logger.error("Error retrieving quotes", exc_info=True)
            return {}

    def add_quote(self, quote_id: int, text: str, author: str) -> None:
        if quote_id in self.model.quotes:
            raise ValueError(f"Quote {quote_id} already exists.")
        self.model.quotes[quote_id] = Quote(id=quote_id, text=text, author=author)
        self.logger.info(f"Added quote {quote_id}")

    def get_optional_categories(self) -> List[str]:
        """
        Return the list of category names that should be marked `.optional`
        in the UI. Pulled from headers.OPTIONAL_CATEGORIES.
        """
        return optional_categories

    def update_quote(self, quote_id: int, text: Optional[str] = None, author: Optional[str] = None) -> None:
        if quote_id not in self.model.quotes:
            raise ValueError(f"Quote {quote_id} not found.")
        q = self.model.quotes[quote_id]
        if text is not None:   q.text = text
        if author is not None: q.author = author
        self.logger.info(f"Updated quote {quote_id}")

    def delete_quote(self, quote_id: int) -> None:
        if quote_id not in self.model.quotes:
            raise ValueError(f"Quote {quote_id} not found.")
        del self.model.quotes[quote_id]
        self.logger.info(f"Deleted quote {quote_id}")

    # -------------------------
    # Rich-text fields
    # -------------------------
    def set_field(self, full_key: str, value: str) -> None:
        if not full_key.startswith("data."):
            self.logger.warning(f"Ignored invalid key: {full_key}")
            return

        # strip "data." and merge into our single quote.data
        nested_key = full_key[len("data."):]
        merge_nested_dict(self.quote.data, nested_key, value)
        self.logger.info(f"set_field {full_key} -> {value!r}")

    def get_field(self, full_key: str) -> Optional[str]:
        if not full_key.startswith("data."):
            return None

        # strip prefix and split path
        nested_key = full_key[len("data."):]
        parts = nested_key.split(".")

        # walk our one quote.data dict
        current: Any = self.quote.data
        for p in parts:
            if isinstance(current, dict) and p in current:
                current = current[p]
            else:
                return None

        return current if isinstance(current, str) else None

    # -------------------------
    # Business logic
    # -------------------------
    def calculate_oee(
        self,
        runtime_hours: float,
        planned_downtime_min: float,
        unplanned_downtime_min: float,
        total_parts: float,
        cycle_time_sec: float,
        total_scrap: float,) -> Dict[str, float]:
        """
        Delegates the heavy lifting to services.oee_service.compute_oee(),
        keeping the original method signature so callers remain unchanged.
        """
        try:
            payload = {
                "runtime":            runtime_hours,
                "planned_downtime":   planned_downtime_min,
                "unplanned_downtime": unplanned_downtime_min,
                "total_parts":        total_parts,
                "cycle_time":         cycle_time_sec,
                "total_scrap":        total_scrap,
            }
            return compute_oee(payload)          # ← one-liner replacement
        except Exception:
            self.logger.error("Error calculating OEE", exc_info=True)
            return {}

    def compute_milestones(self, cost_grid_file: str) -> Dict[str, int]:
        """
        Given the path to your Excel cost grid, uses ProjectMilestonesCalculator
        to compute and return the milestone values.
        """
        try:
            self.logger.info(f"[LOADING] Computing milestones from {cost_grid_file}")
            calc = ProjectMilestonesCalculator(cost_grid_file)
            calc.compute_d_column()
            calc.compute_final_values()
            return calc.final_values.__dict__
        except Exception:
            self.logger.error("Error computing milestones", exc_info=True)
            raise

    def spell_check_categories(self) -> List[str]:
        """
        Returns the list of categories for which spell‐check should be enabled
        (pulled from models.headers.spellcheck_categories).
        """
        return spellcheck_categories

    def spell_check_quote(self, text: Optional[str] = None) -> Dict[str, Any]:
        sc = SpellCheckerService()
        target = text or " ".join(q.text for q in self.model.quotes.values())
        return sc.check_text(target)
        
    def get_project_cost(self, cost_grid_file: str) -> str:
        """
        Retrieves the project cost with no decimals and returns it as a string.
        """
        self.logger.info("[LOADING] Calculating project cost")
        try:
            calc = ProjectMilestonesCalculator(cost_grid_file)
            raw_cost = calc.get_project_cost()
            # Format with commas, no decimals
            formatted_cost = f"${raw_cost:,.0f}"
            return formatted_cost

        except Exception as e:
            raise e

    # -------------------------
    # Persistence
    # -------------------------
    def get_all_fields(self) -> Dict[str, str]:
        """
        Flatten self.quote.data into a map of full_key → string,
        e.g. "data.ShippingInformation.incoterm" → "FOB".
        """
        if not self.quote.data:
            return {}
        return self.quote.data


    def set_all_fields(self, flat_map: Dict[str, str]) -> None:
        # ensure a Quote exists
        if not self.model.quotes:
            self.model.quotes[1] = Quote(id=1, text="", author="")
            self.logger.info("Auto-initialized blank quote")

        applied = 0
        for full_key, val in flat_map.items():
            if not full_key.startswith("data."):
                self.logger.warning(f"Ignoring invalid key: {full_key}")
                continue

            # Delegate to set_field so we get logging + proper merge
            self.set_field(full_key, val)
            applied += 1

        self.logger.info(f"set_all_fields: applied {applied} entries")


    

    def save_quote(self, filename: str, quote_type: str) -> None:
        """
        Persist the current quote to XML. Ensures nested structure before saving.
        Overwrites the Quote.data with the most current version from JS,
        then delegates to the model.
        """
        # 1. Get all fields from JS (flat dict)
        js_fields = self.get_all_fields()
        self.logger.info(f"[save_quote] Received flat fields from JS: {list(js_fields.keys())[:10]}... total {len(js_fields)} keys")

        # 2. If flat, convert to nested using handler's static unflatten_dict
        if all("." in k for k in js_fields):
            self.logger.info("[save_quote] All keys are flat, calling handler._unflatten_dict to nest data.")
            nested = WordSubmissionHandler._unflatten_dict(js_fields)
            self.logger.info(f"[save_quote] Nested dict keys: {list(nested['data'].keys())[:10]}...")

            # Actually store the nested data
            self.quote.data = nested['data']
        else:
            self.logger.info("[save_quote] Data already nested, storing as-is.")
            self.quote.data = js_fields

        # 3. Log current data (truncated for safety)
        preview_keys = list(self.quote.data.keys()) if isinstance(self.quote.data, dict) else type(self.quote.data)
        self.logger.info(f"[save_quote] Quote.data (preview keys): {preview_keys}")

        # 4. Print to stdout for debug trace (optional)
        print("[SAVING] ", self.quote)

        # 5. Delegate to the model to serialize to XML
        self.logger.info(f"[save_quote] Calling model.save_to_xml({filename!r}, {quote_type!r}) ...")
        self.quote.id = 0
        self.model.quotes[0] = self.quote   
        print("MODEL dict before saving:", self.quote.id, self.model.quotes)

        self.model.save_to_xml(filename, quote_type)
        self.logger.info(f"[save_quote] model.save_to_xml completed for {filename!r}")


        
    def load_quote(self, filename: str) -> Dict[int, Dict[str, Any]]:
        # 1) load from XML into self.quote.data
        self.model.load_from_xml(filename)
        # 2) return full quotes dict to the bridge; 
        #    JS can then call get_all_fields() to repopulate its store
        return self.get_quotes()

    def get_contact_by_id(self, contact_id):
        """Fetch contact info from the DB by ID (returns dict or None)."""
        try:
            with self.db_manager.get_connection("contacts") as conn:
                cur = conn.cursor()
                cur.execute(
                    "SELECT name, email, title, phone FROM contacts WHERE id = ?", (contact_id,)
                )
                row = cur.fetchone()
                if row:
                    return dict(zip(["name", "email", "title", "phone"], row))
        except Exception as e:
            self.logger.error(f"Error fetching contact by ID {contact_id}: {e}", exc_info=True)
        return None

    def hydrate_customer_contact(self, customercontact: dict) -> dict:
        """
        Ensure data.customercontact has real fields. Uses 'telephone' for phone.
        """
        return self.hydrate_contact_fields(customercontact, phone_key="telephone")


    def hydrate_alliance_contact(self, alliancecontact: dict) -> dict:
        """
        Ensure data.alliancecontact has real fields. Uses 'cell' for phone.
        """
        return self.hydrate_contact_fields(alliancecontact, phone_key="cell")





    def submit_quote(
            self,
            template_path: str,
            output_path: str,
            status_callback=None,
        ) -> None:
        """
        Submits the current quote for Word template generation.

        This method now ensures the context dict is wrapped as {'data': ...}
        so that Jinja2 templates expecting 'data.' as the root will work,
        AND flattens systemDesc to match template expectations.
        """
        handler = WordSubmissionHandler(template_path, status_callback=status_callback)
        first_quote = next(iter(self.model.quotes.values()))
        self.logger.info(f"first_quote.data:  {first_quote.data}")

        # Ensure the context is always wrapped as 'data'
        # Make a shallow copy of your data to avoid mutating the original
        # Make a shallow copy of your data to avoid mutating the original
        data_copy = dict(first_quote.data)

        # Add the quoteType key
        data_copy["quoteType"] = self.quote_type

        # Hydrate customer contact (ID -> fields; uses 'telephone')
        if "customercontact" in data_copy and isinstance(data_copy["customercontact"], dict):
            data_copy["customercontact"] = self.hydrate_customer_contact(data_copy["customercontact"])

        # Hydrate alliance contact (ID -> fields; uses 'cell')
        if "alliancecontact" in data_copy and isinstance(data_copy["alliancecontact"], dict):
            data_copy["alliancecontact"] = self.hydrate_alliance_contact(data_copy["alliancecontact"])

        # Wrap for Jinja
        jinja_data = {"data": data_copy}

        # Flatten systemDesc if it exists
        if "systemDesc" in jinja_data["data"]:
            jinja_data["data"]["systemDesc"] = self.flatten_system_desc(jinja_data["data"]["systemDesc"])

        if not output_path.lower().endswith(".docx"):
            output_path += ".docx"

        handler.render_document(jinja_data, output_path)



    def flatten_system_desc(self, system_desc):
        """
        Flattens a nested system_desc dict to use keys like 'name.1', 'description.1' for template compatibility.
        """
        flat = {}
        for k, v in system_desc.items():
            if isinstance(v, dict):
                for idx, val in v.items():
                    flat[f"{k}.{idx}"] = val
            else:
                flat[k] = v
        return flat




    # -------------------------
    # Alliance contacts CRUD
    # -------------------------
    def get_alliance_contacts(self) -> List[Dict[str, Any]]:
        try:
            with self.db_manager.get_connection("contacts") as conn:
                rows = conn.execute(
                    "SELECT id, name, email, title, phone FROM contacts"
                ).fetchall()
                # Correct mapping: r[2] = email, r[3] = title
                return [
                    {"id": r[0], "name": r[1], "email": r[2], "title": r[3], "phone": r[4]}
                    for r in rows
                ]
        except Exception as e:
            self.logger.error("Error loading contacts", exc_info=True)
            return []

    def hydrate_contact_fields(self, contact_obj: dict, phone_key: str) -> dict:
        """
        Given a contact object where .name may be an ID, replace it with real fields.
        Sets .name, .email, .title and a phone under `phone_key` ('telephone' or 'cell').
        Leaves other keys intact.
        """
        try:
            if not isinstance(contact_obj, dict):
                return contact_obj

            name_val = contact_obj.get("name")
            # If it's an integer-ish ID, look up; if it's already a string name, use as-is
            try:
                cid = int(name_val)
            except (TypeError, ValueError):
                # Already a name; nothing to look up
                return contact_obj

            row = self.get_contact_by_id(cid)  # returns dict: name, email, title, phone
            if not row:
                self.logger.warning(f"No contact found for ID={cid}")
                return contact_obj

            contact_obj["name"] = row.get("name", "")
            contact_obj["email"] = row.get("email", "")
            contact_obj["title"] = row.get("title", "")
            contact_obj[phone_key] = row.get("phone", "")
            # Remove any stray phone key if present to avoid confusion in templates
            if phone_key != "phone" and "phone" in contact_obj:
                contact_obj.pop("phone", None)
            return contact_obj
        except Exception as e:
            self.logger.error(f"Error hydrating contact fields: {e}", exc_info=True)
            return contact_obj

    def add_alliance_contact(self, contact: Dict[str, Any]) -> int:
        try:
            with self.db_manager.get_connection("contacts") as conn:
                cursor = conn.execute(
                    "INSERT INTO contacts (name,  email, title, phone) VALUES (?, ?, ?,?)",
                    (contact["name"], contact["email"],contact["title"], contact["phone"])
                )
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error("Error adding contact", exc_info=True)
            raise

    def update_alliance_contact(self, contact: Dict[str, Any]) -> None:
        try:
            with self.db_manager.get_connection("contacts") as conn:
                conn.execute(
                    "UPDATE contacts SET name = ?, email = ?, title = ?, phone = ? WHERE id = ?",
                    (contact["name"], contact["email"], contact["title"], contact["phone"], contact["id"])
                )
                conn.commit()
        except Exception as e:
            self.logger.error("Error updating contact", exc_info=True)
            raise

    def delete_alliance_contact(self, contact_id: int) -> None:
        try:
            with self.db_manager.get_connection("contacts") as conn:
                conn.execute(
                    "DELETE FROM contacts WHERE id = ?",
                    (contact_id,)
                )
                conn.commit()
        except Exception as e:
            self.logger.error("Error deleting contact", exc_info=True)
            raise

    # -------------------------
    # Application settings
    # -------------------------
    def get_app_settings(self) -> Dict[str, Any]:
        """
        Load all visible settings from the settings DB and return only JSON-safe types.
        """
        result: Dict[str, Any] = {}
        for key in Settings.get_visible_settings():
            val = self.db_manager.get_setting(key)
            if val is None:
                val = getattr(Settings, key, None)

            # ★ NEW – convert any Path object coming from Settings to str
            if isinstance(val, Path):
                val = str(val)

            result[key] = val
        return result

    def update_app_settings(self, new_settings: Dict[str, Any]) -> None:
        """
        Persist each user-editable setting, then refresh storage paths if
        the DB or log folder changed. EXTREMELY VERBOSE LOGGING VERSION.
        """
        import traceback
        from pprint import pformat

        # Announce function entry
        print("[update_app_settings] ENTERED with settings:")
        self.logger.info(f"[update_app_settings] Called with settings:\n{pformat(new_settings)}")

        # Step 1: Iterate and persist all settings
        for key, value in new_settings.items():
            print(f"[update_app_settings] Processing key={repr(key)}, value={repr(value)}")
            try:
                # Update in-memory static value
                print(f"    [in-memory] setattr(Settings, {key}, {repr(value)})")
                setattr(Settings, key, value)
                self.logger.info(f"    Set in-memory: {key} = {repr(value)}")

                # Attempt DB persistence
                print(f"    [db] self.db_manager.set_setting({key}, {repr(value)})")
                self.db_manager.set_setting(key, str(value))
                self.logger.info(f"    Persisted to DB: {key} = {repr(value)}")

            except Exception as e:
                msg = (
                    f"[update_app_settings][ERROR] Failed to persist key={key}, value={repr(value)}\n"
                    f"Exception: {str(e)}\n{traceback.format_exc()}"
                )
                print(msg)
                self.logger.error(msg)

        # Step 2: Show the new DB and LOG folder values (after update)
        db_folder = getattr(Settings, "DB_FOLDER_PATH", None)
        log_folder = getattr(Settings, "LOG_FOLDER_PATH", None)
        print(f"[update_app_settings] After update: DB_FOLDER_PATH={repr(db_folder)}, LOG_FOLDER_PATH={repr(log_folder)}")
        self.logger.info(f"[update_app_settings] After update: DB_FOLDER_PATH={repr(db_folder)}, LOG_FOLDER_PATH={repr(log_folder)}")

        # Step 3: Update storage root and log the results
        try:
            new_storage_root = str(Path(Settings.DB_FOLDER_PATH).parent)
            print(f"[update_app_settings] Calling Settings.update_storage_root({new_storage_root})")
            self.logger.info(f"[update_app_settings] Calling Settings.update_storage_root({new_storage_root})")
            Settings.update_storage_root(new_storage_root)
            print("[update_app_settings] Storage root updated successfully.")
            self.logger.info("[update_app_settings] Storage root updated successfully.")
        except Exception as e:
            msg = (
                f"[update_app_settings][ERROR] Failed to update storage root using DB_FOLDER_PATH={repr(db_folder)}\n"
                f"Exception: {str(e)}\n{traceback.format_exc()}"
            )
            print(msg)
            self.logger.error(msg)

        print("[update_app_settings] FINISHED.\n")
        self.logger.info("[update_app_settings] FINISHED.")
