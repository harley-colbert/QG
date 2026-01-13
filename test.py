import inspect

print("=== html-for-docx introspection ===")
try:
    import html4docx
    print("Imported html4docx module:", dir(html4docx))

    # Check for HtmlToDocx class
    if hasattr(html4docx, "HtmlToDocx"):
        print("HtmlToDocx FOUND")
        parser = html4docx.HtmlToDocx()
        print("HtmlToDocx methods:", [m for m in dir(parser) if not m.startswith("_")])

        # Inspect the signature of add_html_to_document
        if hasattr(parser, "add_html_to_document"):
            print("add_html_to_document signature:",
                  inspect.signature(parser.add_html_to_document))

except ImportError as e:
    print("Failed to import html4docx:", e)
