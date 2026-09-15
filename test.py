# =====================================================================
# 1. SETUP DUMMY DATA & THRESHOLD
# =====================================================================
# This is our minimum passing grade. Only scores >= 0.70 will pass.
SIMILARITY_THRESHOLD = 0.70

# This simulates raw search results containing (Document Text, Match Score)
results_with_scores = [
    ("Document A: Python is a popular programming language.", 0.85),
    ("Document B: Heavy rain is expected in Seattle tomorrow.", 0.42),
    ("Document C: Python syntax uses clean indentations.", 0.71)
]

print("=== STARTING THE FILTERING PROCESS ===")
print(f"Target Similarity Threshold: {SIMILARITY_THRESHOLD}\n")
print(f"Total documents to inspect: {len(results_with_scores)}")
print("-" * 50)

# =====================================================================
# 2. FILTERING PROCESS WITH CHECKPOINT PRINTS
# =====================================================================
# We will use a standard 'for loop' here instead of a list comprehension 
# so we can print checkpoints for every single step.

filtered = []  # This list will hold our passing documents

for index, (doc, score) in enumerate(results_with_scores, start=1):
    print(f"\n[CHECKPOINT] Checking Document #{index}...")
    print(f"  -> Content Snippet: '{doc[:45]}...'")
    print(f"  -> Similarity Score: {score}")
    
    # Evaluate the score against our threshold rule
    if score >= SIMILARITY_THRESHOLD:
        print(f"  -> VERDICT: [PASS] {score} is greater than or equal to {SIMILARITY_THRESHOLD}")
        filtered.append((doc, score))
        print(f"  -> Action: Added Document #{index} to the filtered list.")
    else:
        print(f"  -> VERDICT: [FAIL] {score} is less than {SIMILARITY_THRESHOLD}")
        print(f"  -> Action: Rejected Document #{index}.")

print("\n" + "-" * 50)
print("=== FILTERING COMPLETED ===")

# =====================================================================
# 3. FINAL OUTPUT SUMMARY
# =====================================================================
print(f"\nOriginal count: {len(results_with_scores)} documents.")
print(f"Filtered count: {len(filtered)} documents passed.")

print("\nFinal 'filtered' list contents:")
for final_doc, final_score in filtered:
    print(f" * [{final_score}] {final_doc}")
