
import matplotlib.pyplot as plt
import numpy as np
import os

os.makedirs("results", exist_ok=True)

methods = ["Standard Pandas", "Pandas Chunking", "Dask"]
times = [115.407813, 115.407813, 111.526876]

# ارتفاع توضيحي للعمود الأول فقط، وليس قياسًا حقيقيًا
display_times = [0, times[1], times[2]]
x = np.arange(len(methods))

fig, ax = plt.subplots(figsize=(10, 6))

bars = ax.bar(
    x,
    display_times,
    color=["lightgray", "steelblue", "orange"],
    width=0.6
)

# العمود الأول: علامة مرئية توضح أن التنفيذ لم يحدث
bars[0].set_height(15)
bars[0].set_hatch("//")
bars[0].set_edgecolor("black")

ax.text(
    0, 17,
    "NOT RUN\n(low RAM)",
    ha="center",
    va="bottom",
    fontsize=9
)

# القيم الحقيقية للطريقتين المكتملتين
ax.text(1, times[1] + 2, f"{times[1]:.2f} s", ha="center")
ax.text(2, times[2] + 2, f"{times[2]:.2f} s", ha="center")

ax.set_xticks(x)
ax.set_xticklabels(methods, rotation=10)
ax.set_ylabel("Execution Time (seconds)")
ax.set_xlabel("Processing Method")
ax.set_title("Execution Time Comparison")
ax.set_ylim(0, 140)

plt.tight_layout()
plt.savefig("results/performance_time.png", dpi=150)
plt.show()
