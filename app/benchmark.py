import time
import statistics
import re
from functools import lru_cache
from app.portfolio import Portfolio

# 1. Load portfolio
# 1. Load benchmark portfolio
portfolio = Portfolio()
portfolio.load_portfolio(
    csv_path="data/benchmark_portfolio.csv"
)

df = portfolio.data
collection = portfolio.collection

print("CSV projects:", len(df))
print("ChromaDB projects:", collection.count())


# 2. Test queries
test_queries = [
    "Python machine learning TensorFlow",
    "React JavaScript frontend development",
    "Java Spring Boot backend development",
    "Android Kotlin mobile development",
    "DevOps Docker Jenkins"
]

# 3. Baseline: Keyword search
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


# 4. Original ChromaDB search
def vector_search_baseline(query):

    return collection.query(
        query_texts=[query],
        n_results=min(2, collection.count())
    )


# 5. Cache query embeddings
embedding_function = collection._embedding_function


@lru_cache(maxsize=256)
def get_cached_embedding(query):

    embedding = embedding_function([query])[0]

    return tuple(float(value) for value in embedding)


# 6. Optimized ChromaDB search
def vector_search_optimized(query):

    query_embedding = get_cached_embedding(query)

    return collection.query(
        query_embeddings=[list(query_embedding)],
        n_results=min(2, collection.count())
    )


# 7. Latency measurement
def measure_latency(search_function, query, repetitions=30):

    search_function(query)  # Warm-up

    timings = []

    for _ in range(repetitions):

        start = time.perf_counter()

        search_function(query)

        end = time.perf_counter()

        timings.append((end - start) * 1000)

    return statistics.median(timings)


# 8. Compare performance
baseline_times = []
optimized_times = []

for query in test_queries:

    # Original implementation
    baseline = measure_latency(
        vector_search_baseline, query
    )

    # Generate embedding once before measuring cache hits
    get_cached_embedding(query)

    # Optimized implementation
    optimized = measure_latency(
        vector_search_optimized, query
    )

    baseline_times.append(baseline)
    optimized_times.append(optimized)

    print(f"\nQuery: {query}")
    print(f"Before optimization: {baseline:.3f} ms")
    print(f"After optimization: {optimized:.3f} ms")


# 9. Calculate averages
avg_before = statistics.mean(baseline_times)
avg_after = statistics.mean(optimized_times)

improvement = (
    (avg_before - avg_after) / avg_before
) * 100 if avg_before else 0


print("\n----- OPTIMIZATION RESULTS -----")
print(f"Before: {avg_before:.3f} ms")
print(f"After: {avg_after:.3f} ms")
print(f"Latency improvement: {improvement:.2f}%")

print("\nEmbedding cache:", get_cached_embedding.cache_info())




print("\n===== RETRIEVAL CORRECTNESS VALIDATION =====")

all_results_match = True

for query in test_queries:

    # Original retrieval
    original_result = vector_search_baseline(query)
    original_ids = original_result["ids"][0]

    # Clear cache to simulate a first-time query
    get_cached_embedding.cache_clear()

    # First-time optimized retrieval
    cold_start = time.perf_counter()
    optimized_first = vector_search_optimized(query)
    cold_latency = (time.perf_counter() - cold_start) * 1000

    optimized_ids = optimized_first["ids"][0]

    # Repeated query with cached embedding
    warm_start = time.perf_counter()
    optimized_repeat = vector_search_optimized(query)
    warm_latency = (time.perf_counter() - warm_start) * 1000

    repeated_ids = optimized_repeat["ids"][0]

    # Compare retrieved project IDs
    same_as_original = original_ids == optimized_ids
    cache_consistent = optimized_ids == repeated_ids

    if not same_as_original or not cache_consistent:
        all_results_match = False

    print(f"\nQuery: {query}")
    print("Original IDs:", original_ids)
    print("Optimized IDs:", optimized_ids)
    print("Repeated IDs:", repeated_ids)
    print(f"First-time latency: {cold_latency:.3f} ms")
    print(f"Cached latency: {warm_latency:.3f} ms")
    print("Matches original:", same_as_original)
    print("Cache consistent:", cache_consistent)

print("\n===== FINAL VALIDATION =====")

if all_results_match:
    print("PASS: All retrieved project IDs match.")
else:
    print("FAIL: Some retrieval results differ.")
