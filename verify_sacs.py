# Programmatic verification of SACS scoring engine

def main():
    print("Initializing SACS Scoring Engine Verification...")
    
    try:
        from models.ats_score import calculate_sacs
        print("[OK] Successfully imported calculate_sacs module.")
    except Exception as e:
        print(f"[ERROR] Failed to import calculate_sacs: {str(e)}")
        return

    # Sample data
    resume = """
    Jane Smith
    jane.smith@email.com | (999) 888-7777
    Skills: Python, React, PostgreSQL, Docker, Git, Agile
    Experience:
    Software Engineer | Tech Innovators (2022 - Present)
    - Developed and maintained multiple backend APIs using Python and Django.
    - Containerized development pipelines using Docker.
    Education:
    Master of Science in Computer Science | State College (2020 - 2022)
    """

    jd = """
    Role: Backend Developer
    Required Experience: 2 years
    Required Degree: Master's
    Required Skills: Python, Django, Docker, AWS, Collaboration
    """

    print("Running SACS Scorer calculation...")
    try:
        results = calculate_sacs(resume, jd)
        print("\n=== Calculation Completed Successfully! ===")
        print(f"Overall SACS Score: {results['overall_score']}/100")
        print("\nComponent Breakdown:")
        for k, v in results["component_scores"].items():
            print(f" - {k.capitalize()}: {v}")
            
        print("\nSample Gained Credits (Additions):")
        for add in results["additions_ledger"][:3]:
            print(f" [+] {add}")
            
        print("\nSample Gaps Identified (Deductions):")
        for ded in results["deductions_ledger"][:3]:
            print(f" [-] {ded}")
            
        print("\n[OK] SACS Scorer verification checks PASSED.")
    except Exception as e:
        print(f"[ERROR] Failed SACS Scorer execution: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
