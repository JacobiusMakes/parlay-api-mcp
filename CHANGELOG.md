# Changelog

## 0.3.7

- Point the packaged README to the latest desktop release and its `-directory.mcpb` asset, so later desktop releases do not leave PyPI readers on a fixed older download.
- Remove the outdated bundle-pending notice from the published package description by including the current README.
- Update Python package and required registry metadata to 0.3.7. Server implementation and dependencies are unchanged from 0.3.6.

The desktop bundle is released separately. The available 0.3.6 directory bundle contains the same server implementation and corrected tool descriptions. This Python documentation release does not rebuild it or change existing client/catalog pins.

## 0.3.6

- Ship the existing checkout-tool description fix: look up current plans with `parlayapi_get_pricing` instead of quoting fixed prices.
- Ship the existing arbitrage-tool description fix: calculations depend on returned quotes and filters, profit is not guaranteed, and availability depends on the requested event, market, and source.
- Include the current public-repository README in the Python package and align registry, Cursor, and LobeHub metadata with 0.3.6.

The server implementation is unchanged from the corrected main branch. No API requests, account actions, or billing behavior are added. The separately locked MCPB remains on 0.3.5 until its dependency lock and bundle can be rebuilt after Python package publication.
