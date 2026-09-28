# Additional requirement

Open this only when reaching the designated stage.


The library must read its documents **once when constructed**. Searches must still work if the original file becomes unavailable. Create a new `Library` to load updated data.

Also preserve input-file order when several documents match, and return `[]` for a negative limit. Assume string queries, integer limits, and valid JSON.

1. Update your task specification.
2. Add a check: copy the synthetic JSON to a temporary folder, construct a library, delete only that temporary copy, then search twice. Both searches should work. Leave the supplied fixture untouched.
3. Verify result order and negative limits.
4. Record the results in your Arena record.
