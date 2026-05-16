# 🖥️ MARIE Calculator Simulator — C Implementation

A software simulation of the **MARIE CPU** (Machine Architecture that is Really Intuitive and Easy) written in C. The simulator replicates every register-transfer operation of a real MARIE processor and prints a full RTL trace for each instruction — so you can see exactly what happens inside the CPU, step by step.

Built as part of a Computer Architecture course at Arab Academy for Science, Technology & Maritime Transport (AAST).

---

## 📌 What is MARIE?

MARIE is a minimal educational CPU architecture designed to teach how computers work at the lowest level. It has:

| Component | Description |
|-----------|-------------|
| **AC** — Accumulator | The only computation register. ALL arithmetic must go through AC. |
| **MAR** — Memory Address Register | Holds the address of the memory cell being accessed. |
| **MBR** — Memory Buffer Register | Holds data being transferred to or from memory. |
| **Memory** | 16 cells. Cell 5 = `OPERAND`, Cell 6 = `TEMP` |
| **Instruction Set** | Only 7 instructions: `INPUT`, `LOAD`, `STORE`, `ADD`, `SUBT`, `CLEAR`, `HALT` |

---

## 🧱 Architecture — 4 Layers

The project is organized into four clean layers, each building on the one below it:

```
┌─────────────────────────────────────────────────────┐
│  Layer 4 — User Interface                            │
│  main() • read_data()                                │
├─────────────────────────────────────────────────────┤
│  Layer 3 — Algorithms                                │
│  marie_sum • marie_average • marie_max • marie_sort  │
├─────────────────────────────────────────────────────┤
│  Layer 2 — High-Level Operations                     │
│  do_add • do_subt • do_clear • marie_set_AC          │
├─────────────────────────────────────────────────────┤
│  Layer 1 — MARIE Primitives                          │
│  exec_input • exec_load • exec_store                 │
│  exec_add • exec_subt • exec_clear • exec_halt       │
└─────────────────────────────────────────────────────┘
```

---

## ⚙️ How It Works

### The TEMP / OPERAND Pattern
Because MARIE has only **one register (AC)**, you can never hold two values at once. Every two-operand operation follows this save-and-restore pattern:

```
1. STORE AC → memory[TEMP]            // save current value
2. INPUT x  → STORE memory[OPERAND]   // load second operand
3. LOAD memory[TEMP] → AC             // restore original value
4. ADD / SUBT memory[OPERAND]         // compute result
```

This pattern is the backbone of every operation in the project.

---

## 🚀 Implemented Operations

### Layer 1 — MARIE Primitive Instructions

| Instruction | What It Does | RTL Trace |
|-------------|-------------|-----------|
| `INPUT` | Read a value into AC | `AC ← value` |
| `LOAD addr` | Load memory[addr] into AC | `MAR ← addr ; MBR ← M[MAR] ; AC ← MBR` |
| `STORE addr` | Save AC into memory[addr] | `MAR ← addr ; MBR ← AC ; M[MAR] ← MBR` |
| `ADD addr` | Add memory[addr] to AC | `MBR ← M[addr] ; AC ← AC + MBR` |
| `SUBT addr` | Subtract memory[addr] from AC | `MBR ← M[addr] ; AC ← AC − MBR` |
| `CLEAR` | Reset AC to zero | `AC ← 0` |
| `HALT` | Stop the processor | Processor stops |

### Layer 2 — High-Level Operations

| Function | Steps | Result |
|----------|-------|--------|
| `do_add(x)` | STORE TEMP → INPUT x → STORE OPERAND → LOAD TEMP → ADD OPERAND | `AC = old_AC + x` |
| `do_subt(x)` | STORE TEMP → INPUT x → STORE OPERAND → LOAD TEMP → SUBT OPERAND | `AC = old_AC − x` |
| `do_clear()` | CLEAR | `AC = 0` |
| `marie_set_AC(v)` | CLEAR → do_add(v) | `AC = v` |

### Layer 3 — Algorithms

**`marie_sum`** — O(n)
```
CLEAR → for each number: do_add(number) → AC = total sum
Example: sum([3, 5, 2]) → AC = 10
```

**`marie_average`** — O(n)
```
marie_sum → avg = AC / count (integer division) → marie_set_AC(avg)
Example: average([1, 2, 4]) → 7 / 3 = 2 → AC = 2
```

**`marie_max`** — O(n) — *compare by subtracting*
```
Set AC = data[0], then for each candidate:
  LOAD current_max → SUBT candidate → if AC < 0: candidate is larger
Example: max([3, 7, 1]) → 3−7 = −4 < 0 → max = 7 → AC = 7
```

**`marie_sort`** — O(n²) Bubble Sort — *swap by subtracting*
```
For each adjacent pair: SUBT → if AC > 0: data[j] > data[j+1] → swap
Example: sort([4, 1, 3]) → [1, 3, 4]
```

> **Key insight:** MARIE has no compare instruction. Instead, subtract: `a − b`. If negative → b is larger. If positive → a is larger. This trick powers both `marie_max` and `marie_sort`.

---

## 🐛 Bug Fixes Applied

| Fix | Description |
|-----|-------------|
| **PC Register Removed** | Unused Program Counter variable removed — C function calls already handle program flow |
| **Integer Average** | `marie_average` was using `double`; fixed to integer division since AC is an integer register |
| **marie_max Uses MARIE Ops** | Old version used a direct C `>` comparison; fixed to use proper `exec_store / exec_load / exec_subt` |
| **do_add / do_subt Verified** | Full 5-step save-restore sequence verified and all intermediate register states printed |

---

## 💻 How to Run

**Requirements:** GCC compiler (any standard C90-compatible compiler)

```bash
# Compile
gcc test2.c -o calc

# Run
./calc
```

The interactive menu will display the current AC value and 8 options:
`ADD`, `SUBT`, `CLEAR`, `SUM`, `AVERAGE`, `MAX`, `SORT`, `EXIT`

Every operation prints a full register-transfer trace showing each `AC`, `MAR`, and `MBR` state change in real time.

---

## 📚 Concepts Covered

- **MARIE CPU architecture** — AC, MAR, MBR, memory layout
- **Register-Transfer Language (RTL)** — tracing every instruction at the hardware level
- **Save-and-restore pattern** — working around the single-register constraint
- **Compare by subtracting** — implementing comparisons without a compare instruction
- **Layered software design** — primitives → operations → algorithms → UI
- **Bubble sort** via MARIE subtraction logic
- **Integer division** in register-constrained architectures

---

## 🛠️ Tools Used

| Tool | Purpose |
|------|---------|
| C (ISO C90) | Implementation language — no external libraries |
| GCC | Compiler |
| VS Code | Code editor |
| Terminal / CMD | Compile and run the simulator |

## 📖 Course

**Computer Architecture** — College of Computing and Information Technology  
Arab Academy for Science, Technology & Maritime Transport (AAST), Cairo, Egypt  
Academic Year: 2025/2026
