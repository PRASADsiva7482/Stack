# 32. Coding Interview Workbook: DSA Patterns and Java Practice

**Status:** Practice workbook.  
**Goal:** Solve common product-company coding problems by recognizing patterns and explaining trade-offs, not by memorizing solutions.

## 1. Coding interview method

For every problem, follow this sequence aloud:

1. Restate the input, output, constraints, and edge cases.
2. Give a brute-force idea and its complexity.
3. Identify the invariant or pattern.
4. Design the optimized algorithm.
5. Dry-run a normal case and a boundary case.
6. Code in Java 17 with clear names.
7. Test empty, singleton, duplicate, sorted, reverse-sorted, overflow, and invalid cases.
8. State time and space complexity and one follow-up variation.

Do not start coding before you can explain why the data structure is needed.

## 2. Pattern recognition table

| Pattern | Recognition signal | Representative exercises |
|---|---|---|
| Hash map/set | Fast membership, frequency, complement, deduplication | Two Sum, Group Anagrams, Longest Consecutive Sequence |
| Two pointers | Sorted array or opposite/end-to-end movement | 3Sum, Container With Most Water, Remove Duplicates |
| Sliding window | Contiguous range with a moving validity condition | Longest Substring, Minimum Window, Max Consecutive Ones |
| Prefix sum | Range sums or balance conditions | Subarray Sum K, Product Except Self, Range Sum |
| Monotonic stack | Next greater/smaller or contribution by boundary | Daily Temperatures, Largest Rectangle, Stock Span |
| Binary search | Monotonic predicate or sorted search space | First/Last Position, Search Rotated, Capacity to Ship |
| Linked list pointers | In-place traversal and cycle/position relationship | Reverse List, Merge Lists, Detect Cycle |
| Heap | Repeated min/max or top-K under streaming input | Kth Largest, Merge K Lists, Median Stream |
| Tree DFS/BFS | Hierarchy, path, depth, level, subtree | Validate BST, LCA, Level Order, Diameter |
| Graph BFS/DFS | Connectivity, reachability, shortest unweighted path | Number of Islands, Clone Graph, Word Ladder |
| Topological sort | Prerequisites and directed dependency order | Course Schedule, Build Order |
| Union-Find | Dynamic connectivity and merging components | Number of Provinces, Redundant Connection |
| Backtracking | Choose, explore, undo; all valid combinations | Permutations, Subsets, N-Queens |
| Greedy | Local choice can be proven safe | Jump Game, Meeting Rooms, Gas Station |
| Dynamic programming | Overlapping subproblems and optimal substructure | House Robber, Coin Change, LCS |
| Trie | Prefix lookup or word dictionary | Implement Trie, Word Search II |
| Intervals | Overlap, merge, schedule, sweep by sorted endpoints | Merge Intervals, Meeting Rooms II |

## 3. Sixty-problem progression

### Set A: foundation (12)

1. Two Sum - hash map invariant.
2. Valid Anagram - frequency map.
3. Contains Duplicate - set.
4. Best Time to Buy and Sell Stock - running minimum.
5. Valid Palindrome - two pointers.
6. Move Zeroes - stable in-place compaction.
7. Valid Parentheses - stack.
8. Binary Search - loop invariant.
9. Reverse Linked List - pointer rewiring.
10. Maximum Depth of Binary Tree - DFS.
11. Flood Fill - graph traversal.
12. Climbing Stairs - one-dimensional DP.

### Set B: product-company medium (24)

13. Group Anagrams.
14. Longest Consecutive Sequence.
15. 3Sum.
16. Longest Substring Without Repeating Characters.
17. Minimum Size Subarray Sum.
18. Subarray Sum Equals K.
19. Product of Array Except Self.
20. Daily Temperatures.
21. Largest Rectangle in Histogram.
22. Search in Rotated Sorted Array.
23. Koko Eating Bananas.
24. Merge Intervals.
25. Non-overlapping Intervals.
26. LRU Cache.
27. Merge Two Sorted Lists.
28. Linked List Cycle II.
29. Reorder List.
30. Kth Largest Element.
31. Top K Frequent Elements.
32. Binary Tree Level Order Traversal.
33. Validate Binary Search Tree.
34. Lowest Common Ancestor.
35. Number of Islands.
36. Rotting Oranges.

### Set C: senior follow-ups (24)

37. Course Schedule - cycle detection/topological order.
38. Network Delay Time - weighted shortest path.
39. Word Ladder - BFS state graph.
40. Accounts Merge - Union-Find.
41. Implement Trie.
42. Word Search - backtracking and visited state.
43. Subsets II - duplicate control.
44. Combination Sum.
45. N-Queens.
46. Jump Game II.
47. Gas Station.
48. Task Scheduler.
49. Meeting Rooms II.
50. House Robber II.
51. Coin Change.
52. Longest Increasing Subsequence.
53. Longest Common Subsequence.
54. Decode Ways.
55. Unique Paths with obstacles.
56. Serialize and Deserialize Binary Tree.
57. Median from Data Stream.
58. Merge K Sorted Lists.
59. Sliding Window Maximum.
60. Design a thread-safe rate limiter.

For each problem record pattern, first wrong idea, final invariant, complexity, edge case missed, and the date of the next retry.

## 4. Java templates

### Binary search on a monotonic predicate

```java
int low = minimumAnswer;
int high = maximumAnswer;
while (low < high) {
    int mid = low + (high - low) / 2;
    if (canComplete(mid)) {
        high = mid;
    } else {
        low = mid + 1;
    }
}
return low;
```

The key is not the syntax; it is proving that `canComplete(x)` changes from false to true only once.

### BFS shortest unweighted path

```java
Deque<Node> queue = new ArrayDeque<>();
Set<Node> visited = new HashSet<>();
queue.add(start);
visited.add(start);
while (!queue.isEmpty()) {
    Node current = queue.removeFirst();
    for (Node next : current.neighbors()) {
        if (visited.add(next)) {
            queue.addLast(next);
        }
    }
}
```

Mark visited when enqueueing to avoid duplicate work. Use a distance field or level loop when the answer depends on path length.

### Sliding window

```java
int left = 0;
for (int right = 0; right < input.length(); right++) {
    add(input.charAt(right));
    while (!windowIsValid()) {
        remove(input.charAt(left++));
    }
    answer = Math.max(answer, right - left + 1);
}
```

State the validity condition and why moving `left` cannot discard a better answer for the current `right`.

## 5. Complexity rules

- A hash map is expected `O(1)`, not a mathematical worst-case guarantee.
- Sorting usually changes a solution to `O(n log n)` but may simplify correctness.
- BFS/DFS is `O(V + E)` with adjacency lists.
- Heap top-K is often `O(n log k)`.
- Dynamic programming complexity is states times transitions; space can often be reduced after proving dependency order.
- Avoid claiming `O(1)` space when recursion depth, output, or visited structures grow with input.

## 6. Timed practice schedule

| Stage | Time | Target |
|---|---:|---|
| Learn | 45 min | Understand pattern and solve with notes |
| Re-solve | 30 min | Implement without notes next day |
| Timed | 35 min | Solve and communicate from a blank editor |
| Review | 15 min | Record invariant, bug, complexity, follow-up |
| Weekly test | 75 min | Two unseen problems plus explanation |

Readiness target: 80% correctness across 10 unseen representative problems, no major edge-case misses, and an explanation that fits in five minutes.

## 7. Coding review checklist

- Did I clarify constraints?
- Is the algorithm correct for duplicates and empty input?
- Did I use `long` where sums can overflow `int`?
- Did I mutate input intentionally?
- Does the loop terminate for every branch?
- Are null and boundary cases handled?
- Are hash keys immutable while stored?
- Is the complexity correct, including sorting and output?
- Can I explain one alternative and why I rejected it?

## 8. Practice tracker

| Problem | Pattern | Attempt 1 | Attempt 2 | Timed pass | Main bug | Next review |
|---|---|---|---|---|---|---|
| Two Sum | Hash map | NOT STARTED | NOT STARTED | NOT STARTED |  |  |
| LRU Cache | Hash map + linked list | NOT STARTED | NOT STARTED | NOT STARTED |  |  |
| Course Schedule | Topological sort | NOT STARTED | NOT STARTED | NOT STARTED |  |  |
| Coin Change | DP | NOT STARTED | NOT STARTED | NOT STARTED |  |  |
| Rate limiter | LLD/concurrency | NOT STARTED | NOT STARTED | NOT STARTED |  |  |

Copy rows for all 60 problems. Do not mark “timed pass” until the code and explanation both pass.

