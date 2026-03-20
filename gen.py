#!/usr/bin/env python

import subprocess
import os
import shutil
from pathlib import Path

if __name__ == "__main__":
    print("=== Master Generator: Solutions to Workspaces ===")
    
    base_dir = Path(__file__).resolve().parent
    exercises_dir = base_dir / "exercises"
    
    homework_dir = base_dir / "homework"
    last_dir = homework_dir / "last"
    
    last_dir.mkdir(parents=True, exist_ok=True)
    
    if not exercises_dir.exists() or not exercises_dir.is_dir():
        print(f"[!] The folder 'exercises' was not found.")
        print(f"    Please create it, add your solution .c files, and try again.")
        input("\nPress Enter to exit...")
        exit()
        
    solution_files = list(exercises_dir.glob("*.c"))
    
    if not solution_files:
        print("[!] No solution .c files found in the 'exercises' folder.")
        input("\nPress Enter to exit...")
        exit()
        
    generated_exercises = []
    generated_tests_count = []
        
    for sol_file in solution_files:
        ex_name = sol_file.stem 
        print(f"\n========================================")
        print(f"--- Processing Solution: {ex_name} ---")
        
        target_dir = last_dir / ex_name
        inputs_dir = target_dir / "inputs"
        outputs_dir = target_dir / "outputs"
        
        target_dir.mkdir(exist_ok=True)
        inputs_dir.mkdir(exist_ok=True)
        outputs_dir.mkdir(exist_ok=True)
        
        temp_exe = target_dir / "temp_solution.exe"
        compile_cmd = ["gcc", str(sol_file), "-o", str(temp_exe)]
        
        print("  Compiling solution...")
        compile_res = subprocess.run(compile_cmd, capture_output=True, text=True)
        
        if compile_res.returncode != 0:
            print(f"  [!] Compilation failed for {sol_file.name}:\n{compile_res.stderr}")
            continue
            
        requirement_lines = []
        in_multiline = False
        
        with open(sol_file, "r", encoding="utf-8") as f_sol:
            for line in f_sol:
                stripped = line.strip()
                
                if not stripped and not in_multiline and not requirement_lines:
                    continue
                    
                if in_multiline:
                    if "*/" in stripped:
                        in_multiline = False
                        text = stripped.replace("*/", "").strip()
                        if text: requirement_lines.append(text)
                    else:
                        if stripped.startswith("*"):
                            stripped = stripped[1:].strip()
                        if stripped: requirement_lines.append(stripped)
                    continue

                if stripped.startswith("//"):
                    requirement_lines.append(stripped[2:].strip())
                elif stripped.startswith("/*"):
                    if "*/" in stripped:
                        text = stripped[2:].replace("*/", "").strip()
                        if text: requirement_lines.append(text)
                    else:
                        in_multiline = True
                        text = stripped[2:].strip()
                        if text: requirement_lines.append(text)
                elif not stripped:
                    if requirement_lines:
                        break
                else:
                    break
                    
        ex_text_console = "\n    ".join(requirement_lines)
        print(f"\n  📝 Requirement:\n    {ex_text_console}\n")
            
        try:
            num_tests = int(input(f"  How many test cases for {ex_name}? "))
        except ValueError:
            print("  [!] Invalid number. Skipping test generation.")
            num_tests = 0
            
        for test in range(1, num_tests + 1):
            print(f"    Enter input for test {test} (Type 'END' on a new line to finish):")
            
            # --- New Multi-line Input Logic ---
            test_input_lines = []
            while True:
                line = input("      > ")
                if line.strip() == "END":
                    break
                test_input_lines.append(line)
                
            test_input = "\n".join(test_input_lines) + "\n"
            
            run_res = subprocess.run(
                [str(temp_exe)],
                capture_output=True,
                text=True,
                input=test_input
            )
            
            with open(inputs_dir / f"{test}.txt", "w") as fin:
                fin.write(test_input)
                
            with open(outputs_dir / f"{test}.txt", "w") as fout:
                fout.write(run_res.stdout)
                
            print(f"      -> Saved inputs/{test}.txt and outputs/{test}.txt\n")
        
        commented_ex_text = "\n".join(f"// {line}" for line in requirement_lines)
        
        boilerplate = f"""{commented_ex_text}

#include <stdio.h>

int main() {{

    return 0;
}}
"""
        with open(target_dir / "main.c", "w", encoding="utf-8") as fmain:
            fmain.write(boilerplate)
        print(f"  -> Created student boilerplate: {ex_name}/main.c")
        
        if temp_exe.exists():
            os.remove(temp_exe)
            
        generated_exercises.append(ex_name)
        generated_tests_count.append(num_tests)
        
    print("\n========================================")
    print("--- Finalizing Package ---")
    meta_path = last_dir / "meta.py"
    
    meta_content = f"""# Automatically generated by the Master Generator
exercise_list = {repr(generated_exercises)}
exercise_count = {len(generated_exercises)}
tests_count = {repr(generated_tests_count)}
"""
    
    with open(meta_path, "w", encoding="utf-8") as meta_file:
        meta_file.write(meta_content)
        
    print(f"  -> Created meta.py with {len(generated_exercises)} exercises registered.")
    
    check_script_src = base_dir / "check.py"
    check_script_dst = last_dir / "check.py"
    
    if check_script_src.exists():
        shutil.copy2(check_script_src, check_script_dst)
        print("  -> Copied check.py into the output folder.")
    else:
        print("  [!] Warning: 'check.py' was not found in the root folder, so it couldn't be copied.")
            
    print(f"\nAll workspaces generated successfully in '{last_dir}'!")
    print("Press Enter to exit...")
    input()