// js/apiWrapper.js

/**
 * This module wraps all window.pywebview.api calls in Promise-based ES6 functions.
 * Use these everywhere in your app to keep UI logic clean and decoupled from pywebview.
 * All functions are exported individually for tree-shaking and clarity.
 */

// ========== File and Folder Browsing ==========

/**
 * Opens a file open dialog to select a file (general).
 * @returns {Promise<string>} Path to selected file, or undefined/cancel.
 */
export async function browseFileField() {
  return window.pywebview.api.browse_file_field();
}

/**
 * Opens a file open dialog for the quote template file.
 * @returns {Promise<string>}
 */
export async function browseTemplateFile() {
  return window.pywebview.api.browse_template_file();
}

/**
 * Opens a folder dialog for the database folder.
 * @returns {Promise<string>}
 */
export async function browseDbFolder() {
  return window.pywebview.api.browse_db_folder();
}

/**
 * Opens a folder dialog for the log folder.
 * @returns {Promise<string>}
 */
export async function browseLogFolder() {
  return window.pywebview.api.browse_log_folder();
}

/**
 * Opens a file save dialog to choose where to save an output file.
 * @param {Object} options { title?: string, default_filename?: string, filetypes?: Array<{description: string, extensions: string[]}> }
 * @returns {Promise<string>} Path to file selected by user, or undefined/cancel.
 */
export async function browseSaveFile({ title, default_filename, filetypes } = {}) {
  // Ensure order: default_filename, title, filetypes (all are positional)
  return window.pywebview.api.browse_save_file()
}




// ========== Category, Field, and View Data ==========

/**
 * Gets the fields that require file browse buttons by category.
 * @returns {Promise<Object>} category-to-fields mapping
 */
export async function getFileBrowseFields() {
  return window.pywebview.api.get_file_browse_fields();
}

/**
 * Gets all optional category names.
 * @returns {Promise<string[]>}
 */
export async function getOptionalCategories() {
  return window.pywebview.api.get_optional_categories();
}

/**
 * Gets the main list of categories for a quote type.
 * @param {string} quoteType "budgetary" or "final"
 * @returns {Promise<string[]>}
 */
export async function getCategories(quoteType) {
  return window.pywebview.api.get_categories(quoteType);
}

/**
 * Gets special lists like incoterms, weeks, etc.
 * @returns {Promise<Object>}
 */
export async function getSpecialLists() {
  return window.pywebview.api.get_special_lists();
}

/**
 * Gets the list of spell-check-enabled categories.
 * @returns {Promise<string[]>}
 */
export async function getSpellCheckCategories() {
  return window.pywebview.api.spell_check_categories();
}

/**
 * Gets field definitions for a given category.
 * @param {string} category
 * @returns {Promise<Object[]>}
 */
export async function getCategoryFields(category) {
  return window.pywebview.api.get_category_fields(category);
}

/**
 * Checks if a category supports dynamic add.
 * @param {string} category
 * @returns {Promise<boolean>}
 */
export async function categoryCanAdd(category) {
  return window.pywebview.api.category_can_add(category);
}

// ========== Quote Operations ==========

/**
 * Creates a new (blank) quote.
 * @returns {Promise<Object>}
 */
export async function newQuote() {
  return window.pywebview.api.new_quote();
}

/**
 * Opens and loads a saved quote.
 * @returns {Promise<Object>}
 */
export async function openQuote() {
  return window.pywebview.api.open_quote();
}

/**
 * Saves the current quote.
 * @param {string} quoteType
 * @returns {Promise<void>}
 */
export async function saveQuote(quoteType) {
  return window.pywebview.api.save_quote(quoteType);
}

// ========== Field Value Operations ==========

/**
 * Sets all fields for a quote from a flat map.
 * @param {Object} flatMap
 * @returns {Promise<void>}
 */
export async function setAllFields(flatMap) {
  return window.pywebview.api.set_all_fields(flatMap);
}

/**
 * Sets a single field value.
 * @param {string} key
 * @param {string} value
 * @returns {Promise<void>}
 */
export async function setField(key, value) {
  return window.pywebview.api.set_field(key, value);
  
}

/**
 * Gets a single field value.
 * @param {string} key
 * @returns {Promise<string>}
 */
export async function getField(key) {
  return window.pywebview.api.get_field(key);
}

/**
 * Clears a single field.
 * @param {string} key
 * @returns {Promise<void>}
 */
export async function clearField(key) {
  return window.pywebview.api.clear_field(key);
}

// ========== OEE and Project Calculations ==========

/**
 * Calculates OEE statistics.
 * @param {Object} payload
 * @returns {Promise<Object>}
 */
export async function calcOee(payload) {
  return window.pywebview.api.calc_oee(payload);
}

/**
 * Gets the project cost for a given file path.
 * @param {string} filePath
 * @returns {Promise<Object>}
 */
export async function getProjectCost(filePath) {
  return window.pywebview.api.get_project_cost(filePath);
}

/**
 * Computes project milestones based on the cost file.
 * @param {string} filePath
 * @returns {Promise<Object>}
 */
export async function computeMilestones(filePath) {
  return window.pywebview.api.compute_milestones(filePath);
}

// ========== App Settings ==========

/**
 * Fetches current application settings.
 * @returns {Promise<Object>}
 */
export async function getAppSettings() {
  return window.pywebview.api.get_app_settings();
}

/**
 * Updates (saves) application settings.
 * @param {Object} settings
 * @returns {Promise<void>}
 */
export async function updateAppSettings(settings) {
  return window.pywebview.api.update_app_settings(settings);
}

// ========== Alliance Contacts CRUD ==========

/**
 * Gets all alliance contacts.
 * @returns {Promise<Object[]>}
 */
export async function getAllianceContacts() {
  return window.pywebview.api.get_alliance_contacts();
}

/**
 * Adds a new alliance contact.
 * @param {Object} contactData
 * @returns {Promise<Object>} The newly added contact.
 */
export async function addAllianceContact(contactData) {
  return window.pywebview.api.add_alliance_contact(contactData);
}

/**
 * Updates an existing alliance contact.
 * @param {Object} contactData
 * @returns {Promise<Object>}
 */
export async function updateAllianceContact(contactData) {
  return window.pywebview.api.update_alliance_contact(contactData);
}

/**
 * Deletes an alliance contact by ID.
 * @param {number} contactId
 * @returns {Promise<void>}
 */
export async function deleteAllianceContact(contactId) {
  return window.pywebview.api.delete_alliance_contact(contactId);
}
