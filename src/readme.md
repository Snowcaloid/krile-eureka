# Services

## Structs

These are model representations of the database records.
They should only contain logic that compares them to other models or retrieves information.

## Providers / GuildProviders

These objects grant read access to the database, such that they load all Structs when they're first used and every time a database change occurs.
They **only** ever **retrieve** information and should **never write information**.

> Providers are Bindables, meaning they store global information that is not relevant to any particular Guild.
>
> GuildProviders are GlobalCollections, meaning they cannot be bound and are to be retrieved by the GuildID-constructor.

## Services / GuildServices

These objects sync the Structs to the database.

To do this, oftentimes a context is needed. [ServiceContext](models/context/__init__.py) contains following information:

* The [Permissions](models/permissions/__init__.py) which the current user has
* The [Logger](../../../utils/logger.py) which should be used as an output or response

The service context also allows simple assertions instead of long/convoluted error-handling routines.

> When a batch sync is happening, it should be done in a `with Transaction()`.
>
> Services are Bindables, meaning they manage global information that is not relevant to any particular Guild.
>
> GuildServices are GlobalCollections, meaning they cannot be bound and are to be retrieved by the GuildID-constructor.

## UserInput

When syncing an object to the database, this is done with certain User inputs. They need to be validated and/or fixed, so that the service can proceed.