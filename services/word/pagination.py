import time
import pythoncom
import win32com.client as win32
from pywintypes import com_error
from .constants import WD_WITHIN_TABLE, logger, LOG_PREFIX

def insert_page_breaks_by_vertical_position(doc_path: str, y_in_inches: float = 7.0):
    c = win32.constants
    threshold_points = y_in_inches * 72
    max_page = 14

    logger.debug(f"{LOG_PREFIX} pagination: open={doc_path!r} y_in={y_in_inches} threshold={threshold_points}pt")
    word = win32.Dispatch("Word.Application")
    word.Visible = False

    pass_count = 0
    inserted_break = True

    while inserted_break:
        inserted_break = False
        try:
            doc = word.Documents.Open(doc_path)
            doc.Repaginate()
            count = doc.Paragraphs.Count
            print(f"\n===== {LOG_PREFIX} Pass #{pass_count + 1} | Paragraph count: {count} =====")
            i = 0
            while i < count - 1:
                para = doc.Paragraphs(i + 1)
                rng = para.Range
                style_name = str(para.Style)
                try:
                    y = rng.Information(c.wdVerticalPositionRelativeToPage)
                    page_num = rng.Information(c.wdActiveEndPageNumber)
                except Exception:
                    y = None
                    page_num = None

                if rng.Information(WD_WITHIN_TABLE):
                    i += 1
                    continue

                if page_num is not None and page_num > max_page:
                    break

                next_para = doc.Paragraphs(i + 2)
                next_rng = next_para.Range
                try:
                    next_y = next_rng.Information(c.wdVerticalPositionRelativeToPage)
                except Exception:
                    next_y = None

                is_heading_1 = style_name.lower() == "heading 1"
                is_bold_start = False
                try:
                    first_word_rng = rng.Words(1)
                    is_bold_start = bool(first_word_rng.Font.Bold)
                except Exception:
                    pass

                if is_heading_1 and y is not None and y > threshold_points:
                    if i > 0:
                        prev_para = doc.Paragraphs(i)
                        insert_rng = prev_para.Range.Duplicate
                        insert_rng.Collapse(c.wdCollapseStart)
                    else:
                        insert_rng = para.Range.Duplicate
                        insert_rng.Collapse(c.wdCollapseStart)
                    insert_rng.Select()
                    word.Selection.InsertBreak(c.wdPageBreak)
                    inserted_break = True
                    break

                if is_bold_start and y is not None and next_y is not None and next_y < y and y > 72:
                    if i > 0:
                        prev_para = doc.Paragraphs(i)
                        insert_rng = prev_para.Range.Duplicate
                        insert_rng.Collapse(c.wdCollapseStart)
                    else:
                        insert_rng = para.Range.Duplicate
                        insert_rng.Collapse(c.wdCollapseStart)
                    insert_rng.Select()
                    word.Selection.InsertBreak(c.wdPageBreak)
                    inserted_break = True
                    break

                i += 1

            doc.Save()
            doc.Close(False)
            del doc
            time.sleep(0.4)
        except com_error as e:
            print(f"{LOG_PREFIX} COM error encountered: {e}. Retrying after sleep...")
            time.sleep(0.75)
            pythoncom.CoInitialize()
            continue
        pass_count += 1

    word.Quit()
