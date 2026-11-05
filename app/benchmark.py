import pandas as pd
import re
import time
import statistics

from app.portfolio import Portfolio

# Load portfolio data
portfolio = Portfolio()
portfolio.load_portfolio()

df = portfolio.data

test_queries = [
    "Python machine learning TensorFlow",
    "React JavaScript frontend development",
    "Java Spring Boot backend development",
    "Android Kotlin mobile development",
    "DevOps Docker Jenkins"
]

# Baseline: keyword-based search
def keyword_search(query):
    query_words = set(re.findall(r"\w+", query.lower()))

    results = []

    for _, row in df.iterrows():
        techstack = str(row["Techstack"]).lower()
        tech_words = set(re.findall(r"\w+", techstack))

        score = len(query_words & tech_words)

        if score > 0:
            results.append((score, row["Links"]))

    results.sort(key=lambda x: x[0], reverse=True)

    return results[:2]


# Optimized: ChromaDB vector search
def vector_search(query):
    count = portfolio.collection.count()

    if count == 0:
        return []

    return portfolio.collection.query(
        query_texts=[query],
        n_results=min(2, count)
    )


# Measure execution time
def measure_latency(search_function, query, repetitions=30):

    # Warm-up call
    search_function(query)

    timings = []

    for _ in range(repetitions):
        start = time.perf_counter()

        search_function(query)

        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        timings.append(elapsed_ms)

    return statistics.median(timings)


baseline_times = []
vector_times = []

for query in test_queries:

    baseline = measure_latency(keyword_search, query)
    vector = measure_latency(vector_search, query)

    baseline_times.append(baseline)
    vector_times.append(vector)

    print(f"\nQuery: {query}")
    print(f"Keyword search: {baseline:.3f} ms")
    print(f"Vector search: {vector:.3f} ms")

avg_baseline = statistics.mean(baseline_times)
avg_vector = statistics.mean(vector_times)

reduction = (
    (avg_baseline - avg_vector) / avg_baseline
) * 100 if avg_baseline else 0

print("\n----- BENCHMARK SUMMARY -----")
print(f"Average baseline latency: {avg_baseline:.3f} ms")
print(f"Average vector latency: {avg_vector:.3f} ms")
print(f"Latency reduction: {reduction:.2f}%")