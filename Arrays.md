# Arrays Patterns & Templates

This page is a practical guide for the most reusable Array-related patterns.

## Solved Array Questions (ordered 1 → n)

<!-- ARRAY_QUESTIONS_START -->

This block is auto-updated by `scripts/update_leetcode_stats.py`.

- Profile: [leetcode.com/devcesarlopes](https://leetcode.com/devcesarlopes)
- Updated at: 2026-04-13 00:38 UTC
- Source: recent accepted submissions filtered by the `array` tag

|   # | LeetCode ID | Problem                                                                                                           |
| --: | ----------: | ----------------------------------------------------------------------------------------------------------------- |
|   1 |          26 | [Remove Duplicates from Sorted Array](https://leetcode.com/problems/remove-duplicates-from-sorted-array/)         |
|   2 |         136 | [Single Number](https://leetcode.com/problems/single-number/)                                                     |
|   3 |         228 | [Summary Ranges](https://leetcode.com/problems/summary-ranges/)                                                   |
|   4 |         268 | [Missing Number](https://leetcode.com/problems/missing-number/)                                                   |
|   5 |        1295 | [Find Numbers with Even Number of Digits](https://leetcode.com/problems/find-numbers-with-even-number-of-digits/) |
|   6 |        1436 | [Destination City](https://leetcode.com/problems/destination-city/)                                               |
|   7 |        2094 | [Finding 3-Digit Even Numbers](https://leetcode.com/problems/finding-3-digit-even-numbers/)                       |
|   8 |        2562 | [Find the Array Concatenation Value](https://leetcode.com/problems/find-the-array-concatenation-value/)           |
|   9 |        2682 | [Find the Losers of the Circular Game](https://leetcode.com/problems/find-the-losers-of-the-circular-game/)       |
|  10 |        2873 | [Maximum Value of an Ordered Triplet I](https://leetcode.com/problems/maximum-value-of-an-ordered-triplet-i/)     |
|  11 |        3471 | [Find the Largest Almost Missing Integer](https://leetcode.com/problems/find-the-largest-almost-missing-integer/) |
|  12 |        3502 | [Minimum Cost to Reach Every Position](https://leetcode.com/problems/minimum-cost-to-reach-every-position/)       |

<!-- ARRAY_QUESTIONS_END -->

## Iteration Templates

### Pattern: Simple Iteration

- Single pointer from `0` to `n-1`.

```python
for i in range(0, n):
	# Do actions stack based on condition
```

![Simple iteration](assets/gifs/array-simple.gif)

### Pattern: Two Pointers (nested scan)

- First pointer `p1` moves from `0` to `n-1`.
- Second pointer `p2` moves from `p1 + 1` to `n-1`.

```python
for p1 in range(0, n):
	for p2 in range(p1 + 1, n):
		# compare/use nums[p1], nums[p2]
```

![Two Pointers iteration](assets/gifs/array-two-pointers.gif)

---

### Pattern: Lazy pointer

- One pointer scans from left to right.
- One write pointer marks the next valid position.

```python
write = 1
for read in range(1, n):
	if condition:
		write += 1
```

![Lazy pointer iteration](assets/gifs/array-lazy-pointer.gif)

---

### Pattern: Matrix traversal

- Matrix scan (`m x n`):

```python
for i in range(0, m):
	for j in range(0, n):
		# process cell (i, j)
```

![Matrix traversal iteration](assets/gifs/array-matrix-traversal.gif)

### Pattern: Matrix traversal + surrounding elements check

- Matrix scan (`m x n`):
- Surrounding-neighbors scan (for each cell):

```python
for i in range(0, m):
	for j in range(0, n):

        for di in [-1, 0, 1]:
            for dj in [-1, 0, 1]:
                ni, nj = i + di, j + dj
                if 0 <= ni < m and 0 <= nj < n:
                    # valid neighbor
```

![Matrix and neighbors iteration](assets/gifs/array-matrix-neighbors.gif)

## 3) Question Templates

### Pattern: Two Pointers (nested scan)

**Sample question:** 1. Two Sum

```python
class Solution:
	def twoSum(self, nums: List[int], target: int) -> List[int]:
		for i in range(0, len(nums)):
			for j in range(i + 1, len(nums)):
				if nums[i] + nums[j] == target:
					return [i, j]
```

### Pattern: Stack

**Sample question:** 20. Valid Parentheses

```python
class Solution:
	def isValid(self, s: str) -> bool:
		stack = deque()
		opens = ['(', '{', '[']
		close_match = {'(': ')', '{': '}', '[': ']'}
		for i in range(len(s)):
			if s[i] in opens:
				stack.append(s[i])
			else:
				if len(stack) == 0:
					return False
				open = stack.pop()
				if close_match[open] != s[i]:
					return False
		return len(stack) == 0
```

### Pattern: In-place Swap / In-place Write Pointer

**Sample question:** 26. Remove Duplicates from Sorted Array

```python
class Solution:
	def removeDuplicates(self, nums: List[int]) -> int:
		k = 1
		for i in range(1, len(nums)):
			if nums[i] != nums[k - 1]:
				nums[i], nums[k] = nums[k], nums[i]
				k += 1
		return k
```

### Pattern: XOR to remove paired elements

**Sample question:** 136. Single Number

```python
class Solution:
	def singleNumber(self, nums: List[int]) -> int:
		x = 0
		for i in range(0, len(nums)):
			x = x ^ nums[i]
		return x
```

### Pattern: Hash Table (dict) counting

**Sample question:** 387. First Unique Character in a String

```python
class Solution:
	def firstUniqChar(self, s: str) -> int:
		table = {}
		for i, c in enumerate(s):
			if c not in table.keys():
				table[c] = 1
			else:
				table[c] += 1
		for i, c in enumerate(s):
			if table[c] == 1:
				return i
		return -1
```

### Pattern: Matrix traversal + surrounding elements check

**Sample question:** 661. Image Smoother

```python
class Solution:
	def imageSmoother(self, img: List[List[int]]) -> List[List[int]]:
		result = [[0] * len(img[0]) for _ in range(len(img))]

		for i in range(0, len(img)):
			for j in range(0, len(img[i])):
				sum = 0
				c = 0
				for di in [-1, 0, 1]:
					for dj in [-1, 0, 1]:
						ni, nj = i + di, j + dj
						if 0 <= ni < len(img) and 0 <= nj < len(img[0]):
							sum += img[ni][nj]
							c += 1
				result[i][j] = sum // c
		return result
```

### Pattern: Iterate over unrepeated indices

**Sample question:** 2094. Finding 3-Digit Even Numbers

```python
class Solution:
	def findEvenNumbers(self, digits: List[int]) -> List[int]:
		l = len(digits)
		nums = set()
		for i in range(0, l):
			for j in range(0, l):
				if i == j:
					continue
				for k in range(0, l):
					if j == k or i == k:
						continue
					n = 100 * digits[i] + 10 * digits[j] + digits[k]
					if n >= 100 and n % 2 == 0:
						nums.add(n)

		return sorted(list(nums))
```
