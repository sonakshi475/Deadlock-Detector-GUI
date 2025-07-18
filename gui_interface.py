import tkinter as tk
from tkinter import messagebox
import subprocess
import os
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# --- GUI Setup ---
window = tk.Tk()
window.title("Deadlock Detector")
window.geometry("700x800")

algo_var = tk.StringVar()

def select_algo():
    algo = algo_var.get()
    if algo == "banker":
        banker_frame.pack(fill="x", pady=10)
        rag_frame.pack_forget()
    elif algo == "rag":
        rag_frame.pack(fill="x", pady=10)
        banker_frame.pack_forget()

def show_plot(fig, title):
    plot_window = tk.Toplevel(window)
    plot_window.title(title)
    canvas = FigureCanvasTkAgg(fig, master=plot_window)
    canvas.draw()
    canvas.get_tk_widget().pack()

def visualize_banker_table(n, m, alloc, maxm, need, avail, result_msg):
    fig, ax = plt.subplots(figsize=(10, n + 3))
    ax.axis("off")

    columns = ["Process", "Max A", "Max B", "Max C", "Alloc A", "Alloc B", "Alloc C",
               "Need A", "Need B", "Need C"]
    table_data = []

    for i in range(n):
        row = [f"P{i}"] + maxm[i] + alloc[i] + need[i]
        table_data.append(row)

    # Append available resources at the bottom
    table_data.append(["Available"] + [""] * 3 + [""] * 3 + avail)

    table = ax.table(cellText=table_data, colLabels=columns, loc='center', cellLoc='center')
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.scale(1, 1.5)
    ax.set_title(f"Banker's Algorithm Table\n{result_msg}", fontsize=14, pad=20)

    show_plot(fig, "Banker's Algorithm Result")

def run_detection():
    algo = algo_var.get()

    if algo == "banker":
        try:
            n = int(entry_p.get())
            m = int(entry_r.get())
            alloc_lines = alloc_text.get("1.0", tk.END).strip().splitlines()
            max_lines = max_text.get("1.0", tk.END).strip().splitlines()
            avail_line = avail_entry.get().strip()

            # Convert inputs to lists
            alloc = [list(map(int, line.split())) for line in alloc_lines]
            maxm = [list(map(int, line.split())) for line in max_lines]
            avail = list(map(int, avail_line.split()))
            need = [[maxm[i][j] - alloc[i][j] for j in range(m)] for i in range(n)]

            # Write to input file
            with open("banker_input.txt", "w") as f:
                f.write(f"{n} {m}\n")
                for row in alloc:
                    f.write(" ".join(map(str, row)) + "\n")
                for row in maxm:
                    f.write(" ".join(map(str, row)) + "\n")
                f.write(" ".join(map(str, avail)) + "\n")

        except Exception as e:
            messagebox.showerror("Input Error", f"Invalid input: {e}")
            return

    elif algo == "rag":
        edges = rag_text.get("1.0", tk.END).strip().splitlines()
        with open("graph.txt", "w") as f:
            f.write(f"{len(edges)}\n")
            for edge in edges:
                f.write(edge + "\n")

    # Write mode to mode.txt
    with open("mode.txt", "w") as f:
        f.write(algo)

    compile = subprocess.run(["g++", "deadlock_detector.cpp", "-o", "deadlock_detector"], capture_output=True, text=True)
    if compile.returncode != 0:
        messagebox.showerror("Compilation Error", compile.stderr)
        return

    run = subprocess.run(["./deadlock_detector"], capture_output=True, text=True)
    if run.returncode != 0:
        messagebox.showerror("Execution Error", run.stderr)
        return

    output = run.stdout.strip()
    messagebox.showinfo("Detection Result", output)

    if algo == "banker":
        visualize_banker_table(n, m, alloc, maxm, need, avail, output)
    elif algo == "rag":
        import networkx as nx
        edges = rag_text.get("1.0", tk.END).strip().splitlines()
        G = nx.DiGraph()
        for edge in edges:
            try:
                u, v = edge.strip().split()
                G.add_edge(u, v)
            except:
                continue
        pos = nx.spring_layout(G)
        fig, ax = plt.subplots(figsize=(6, 5))
        nx.draw(G, pos, with_labels=True, node_color='skyblue', edge_color='gray', node_size=2000, font_size=10, ax=ax)
        if "Deadlock" in output:
            try:
                cycle = nx.find_cycle(G, orientation='original')
                cycle_edges = [(u, v) for u, v, _ in cycle]
                nx.draw_networkx_edges(G, pos, edgelist=cycle_edges, edge_color='r', width=2, ax=ax)
            except:
                pass
        ax.set_title("Resource Allocation Graph")
        show_plot(fig, "RAG Visualization")

# --- GUI Layout ---
tk.Label(window, text="Select Algorithm:").pack()
tk.Radiobutton(window, text="Banker's Algorithm", variable=algo_var, value="banker", command=select_algo).pack()
tk.Radiobutton(window, text="RAG Detection", variable=algo_var, value="rag", command=select_algo).pack()

banker_frame = tk.Frame(window)
tk.Label(banker_frame, text="Number of Processes:").pack()
entry_p = tk.Entry(banker_frame)
entry_p.pack()

tk.Label(banker_frame, text="Number of Resources:").pack()
entry_r = tk.Entry(banker_frame)
entry_r.pack()

tk.Label(banker_frame, text="Allocation Matrix (each row space-separated):").pack()
alloc_text = tk.Text(banker_frame, height=5, width=50)
alloc_text.pack()

tk.Label(banker_frame, text="Max Matrix (each row space-separated):").pack()
max_text = tk.Text(banker_frame, height=5, width=50)
max_text.pack()

tk.Label(banker_frame, text="Available Resources (space-separated):").pack()
avail_entry = tk.Entry(banker_frame, width=50)
avail_entry.pack()

rag_frame = tk.Frame(window)
tk.Label(rag_frame, text="Enter Edges (e.g. P0 R0):").pack()
rag_text = tk.Text(rag_frame, height=10, width=50)
rag_text.pack()

tk.Button(window, text="Run Deadlock Detection", command=run_detection).pack(pady=20)

window.mainloop()
