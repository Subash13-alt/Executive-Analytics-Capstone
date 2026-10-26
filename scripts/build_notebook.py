"""Compile analysis_cells.py into an executed .ipynb (plain JSON, no nbformat needed)."""
import json, re, io, base64, contextlib, sys, traceback
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt

src = open("scripts/analysis_cells.py").read()
chunks = re.split(r"^# %%", src, flags=re.M)[1:]
ns, cells, count = {"__name__": "__main__"}, [], 0

def lines(t): 
    ls = t.split("\n"); return [l + "\n" for l in ls[:-1]] + [ls[-1]]

for ch in chunks:
    if ch.startswith(" [markdown]"):
        body = ch[len(" [markdown]"):].strip("\n")
        md = "\n".join(l[2:] if l.startswith("# ") else l.lstrip("#") if l.strip() == "#" else l for l in body.split("\n"))
        cells.append({"cell_type": "markdown", "metadata": {}, "source": lines(md)})
        continue
    code = ch.strip("\n"); count += 1
    buf, outputs = io.StringIO(), []
    with contextlib.redirect_stdout(buf):
        try: exec(compile(code, f"cell{count}", "exec"), ns)
        except Exception: traceback.print_exc(file=sys.stderr); raise
    if buf.getvalue():
        outputs.append({"output_type": "stream", "name": "stdout", "text": lines(buf.getvalue().rstrip("\n") + "\n")})
    for n in plt.get_fignums():
        f = io.BytesIO(); plt.figure(n).savefig(f, format="png", dpi=110, bbox_inches="tight")
        outputs.append({"output_type": "display_data", "metadata": {},
                        "data": {"image/png": base64.b64encode(f.getvalue()).decode(), "text/plain": ["<Figure>"]}})
        if count == 6 or True: plt.figure(n).savefig(f"outputs/fig_cell{count}.png", dpi=130, bbox_inches="tight")
    plt.close("all")
    cells.append({"cell_type": "code", "metadata": {}, "execution_count": count, "source": lines(code), "outputs": outputs})

nb = {"cells": cells, "metadata": {"kernelspec": {"display_name": "Python 3", "language": "python", "name": "python3"},
      "language_info": {"name": "python"}}, "nbformat": 4, "nbformat_minor": 5}
json.dump(nb, open("churn_segmentation_analysis.ipynb", "w"), indent=1)
print("notebook written,", count, "code cells")
