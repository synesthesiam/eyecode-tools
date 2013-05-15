#!/usr/bin/env python
import os, sys, argparse, json, sha, base64, re

# Directory to save image files
IMAGE_DIR = "img"

# Prefix for Markdown image URLs
IMAGE_URL_PREFIX = "img"

def cleanup(s):
    return re.sub(r"[^0-9a-zA-Z]+", "", s)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("notebook", type=str, help="Path to IPython notebook file (.ipynb)")
    parser.add_argument("--output", type=str, default=None, help="Path to output file (default: stdout)")
    args = parser.parse_args()

    out = sys.stdout
    if args.output is not None:
        out = open(args.output, "w")

    # Import notebook JSON
    notebook = json.load(open(args.notebook, "r"))

    # Only one worksheet is supported
    cells = notebook["worksheets"][0]["cells"]
    in_code = False

    # Output each cell
    for cell in cells:
        if cell["cell_type"] == "markdown":
            # Write markdown directly
            for line in cell["source"]:
                print >>out, line.rstrip()
            print >>out, ""

        elif cell["cell_type"] == "code":
            # Wrap code in Github fenced code block
            print >>out, "```python"
            for line in cell["input"]:
                print >>out, line.rstrip()
            print >>out, "```"
            print >>out, ""

            # Write cell output
            outputs = cell["outputs"]
            if len(outputs) > 0:
                print >>out, ""
                print >>out, "**Output**:"
                print >>out, ""

                output_types = [o["output_type"] for o in outputs]

                # Write as a fenced code block with no highlighting
                if ("pyout" in output_types) or ("stream" in output_types):
                    print >>out, "```"
                    for output in cell["outputs"]:
                        if output["output_type"] in ["pyout", "stream"]:
                            for line in output["text"]:
                                print >>out, line.rstrip()
                            print >>out, "```"
                            print >>out, ""

                # Save base64-encoded PNG to the file system.
                # The file name is just the SHA hash of the raw image data prefixed with "gen_".
                if "display_data" in output_types:
                    for output in cell["outputs"]:
                        if output["output_type"] == "display_data":
                            image_data = base64.decodestring(output["png"])
                            image_id = "gen_" + cleanup(base64.encodestring(sha.sha(image_data).digest())[:-2])
                            image_path = os.path.join(IMAGE_DIR, "{0}.png".format(image_id))
                            with open(image_path, "wb") as image_file:
                                image_file.write(image_data)
                            print >>out, "![]({0}/{1}.png)".format(IMAGE_URL_PREFIX, image_id)
                            print >>out, ""

    out.close()
