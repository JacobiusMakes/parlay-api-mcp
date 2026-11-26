# Check one sport on the public board

Does the board currently list the sport your project needs? The public MCP tool returns sport keys and event counts. This check uses the installed server, makes one public data request and works without an account, API key or language model.

## Run the example

From a checkout of this repository, install the server in a Python virtual environment and run the example.

```sh
python -m pip install 'parlayapi-mcp==0.3.8'
python examples/first_board_check.py basketball_nba
```

The output includes the requested sport key, status, event count, tool name and UTC receipt time. A listed row with a count of zero stays zero. An absent row produces `not_listed` and a null count. A listed row with a missing or invalid count produces `count_unknown`. A tool error exits without recording an observation. [Example source](../examples/first_board_check.py)

## Try it in your MCP client

With ParlayAPI connected, paste this request and substitute the sport key you need.

> Check whether the public board lists `basketball_nba`. Call only `parlayapi_live_sports`, once. Match the exact sport key and report the returned event count, with the tool name as its source. If the row or count is missing, say which is missing. If the call fails, report the error and stop. Leave account tools unused.

## Interpret the answer

Suppose a fictional board returns `{"key":"basketball_nba","event_count":3}`. That supports the sentence “The board listed three NBA events when checked.” It gives you no bookmaker, period, market, price or quote timestamp. A request to show *a current NBA price* still needs the event, bookmaker, market, period and outcome before choosing an odds lookup. If the selected outcome has a null price, leave the price unknown.

For a project that already has a specific odds row, the [evaluation lab](https://parlay-api.com/tools/evaluation-lab) lets you check the fields that matter to your application.
