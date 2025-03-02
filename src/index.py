import asyncio
import os

if (
    # The WERKZEUG_RUN_MAIN is set to true when running the subprocess for
    # reloading, we want to start debugpy only once during the first
    # invocation and never during reloads.
    os.environ.get("WERKZEUG_RUN_MAIN") != "true"
):
    import debugpy

    debugpy.listen(("0.0.0.0", 5678))
    debugpy.wait_for_client()

    from dotenv import load_dotenv
    # Load all environment variables before doing anything else
    load_dotenv()

    if os.getenv('WAIT_DEBUG').upper() == 'TRUE':
        print('Waiting for Debugger to attach.')
        debugpy.wait_for_client()

    from data.db.definition import TableDefinitions

    # initialize all tables before anything else is done
    # this way the order of loading of any global data class is irrelevant
    TableDefinitions()

    import bot

    client = bot.Krile()

    async def main():
        await client.start(os.getenv('DISCORD_TOKEN'))

    asyncio.run(main())
