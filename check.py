#!/usr/bin/env python

import subprocess
import getpass
from pathlib import Path
from meta import exercise_list, exercise_count, tests_count

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

if __name__ == "__main__":
    try:
        print(f"{CYAN}Starting checker...{RESET}")
        results = []
        
        base_dir = Path(__file__).resolve().parent

        current_ex = 1
        for exercise in exercise_list:
            exercise_dir = base_dir / exercise
            c_files = [str(file) for file in exercise_dir.glob("*.c")]
            
            if not c_files:
                results.append(subprocess.CompletedProcess(args=[], returncode=1, stderr="No .c files found."))
                current_ex += 1
                continue
                
            output_exe = str(exercise_dir / "main.exe")
            command = ["gcc"] + c_files + ["-o", output_exe]
            
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False
            )

            results.append(result)
            print(f"\rChecked: {current_ex}/{exercise_count} exercises.", end='')
            current_ex += 1

        print("\n\n")

        all_passed = True
        current_result = 0
        
        for result in results:
            current_result += 1
            exercise_name = exercise_list[current_result - 1]
            exercise_dir = base_dir / exercise_name

            print(f"{CYAN}{BOLD}{'='*50}{RESET}")
            print(f"{CYAN}{BOLD}Testing Exercise {current_result}: {exercise_name}{RESET}")
            print(f"{CYAN}{BOLD}{'='*50}{RESET}")

            if result.returncode != 0:
                all_passed = False
                print(f"{RED}{BOLD}Exercise {current_result} failed to compile.{RESET}")
                print(f"{YELLOW}Check for syntax errors:\n{result.stderr}{RESET}\n")
                continue

            exe_path = str(exercise_dir / "main.exe")
            exercise_passed = True

            for test in range(1, tests_count[current_result - 1] + 1):
                input_path = exercise_dir / "inputs" / f"{test}.txt"
                
                with open(input_path, "r") as f:
                    input_text = f.read()
                
                output = subprocess.run(
                    [exe_path],
                    capture_output=True,
                    text=True,
                    check=False,
                    input=input_text
                )

                output_path = exercise_dir / "outputs" / f"{test}.txt"
                with open(output_path) as expected_file:
                    expected = expected_file.read()
                    
                    if output.stdout.strip() != expected.strip():
                        all_passed = False
                        exercise_passed = False
                        print(f"\n{RED}{BOLD}[-] Exercise {current_result} failed on test case {test}.{RESET}")
                        
                        print(f"Input:{RESET}")
                        for line in input_text.strip().splitlines():
                            print(f"\t{line}")
                            
                        print(f"{RED}Output (Yours):{RESET}")
                        for line in output.stdout.strip().splitlines():
                            print(f"\t{line}")
                            
                        print(f"{RED}Expected:{RESET}")
                        for line in expected.strip().splitlines():
                            print(f"\t{line}")
                        print(f"{CYAN}{'-' * 50}{RESET}")
                    else:
                        print(f"{GREEN}[+] Test case {test} passed.{RESET}")

            if exercise_passed:
                print(f"\n{GREEN}{BOLD}Exercise {current_result} passed all tests!{RESET}\n")
            else:
                print(f"\n{RED}{BOLD}Exercise {current_result} had failing tests.{RESET}\n")

        print(f"{CYAN}{BOLD}{'='*50}{RESET}")
        if all_passed:
            print(f"{GREEN}{BOLD}All tests passed. Homework complete!{RESET}\n")
        else:
            print(f"{RED}{BOLD}Some tests failed. Keep debugging!{RESET}\n")

        while(getpass.getpass("\rPress enter to exit...") != ''): pass
        
    except Exception as e:
        print(f"{RED}{BOLD}Checker failed with the following error:\n{e}{RESET}")
        while(getpass.getpass("\rPress enter to exit...") != ''): pass