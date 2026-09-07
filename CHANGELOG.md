# Changelog

## 0.3.6

- Ship the existing checkout-tool description fix: look up current plans with `parlayapi_get_pricing` instead of quoting fixed prices.
- Ship the existing arbitrage-tool description fix: calculations depend on returned quotes and filters, profit is not guaranteed, and availability depends on the requested event, market, and source.
- Include the current public-repository README in the Python package and align registry, Cursor, and LobeHub metadata with 0.3.6.

The server implementation is unchanged from the corrected main branch. No API requests, account actions, or billing behavior are added. The separately locked MCPB remains on 0.3.5 until its dependency lock and bundle can be rebuilt after Python package publication.
