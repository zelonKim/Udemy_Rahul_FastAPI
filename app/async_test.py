from rich import print
import time
import asyncio


async def endpoint(route: str) -> str:
    print(f">> handling {route}")

    await asyncio.sleep(1)

    print(f"<< response {route}")
    return route


async def server():
    tests = ("GET /shipment/1", "PATCH /shipment/4", "GET /shipment/3")

    start = time.perf_counter()


    # requests = [asyncio.create_task(endpoint(route)) for route in tests]

    # done, pending = await asyncio.wait(requests)

    # for task in done:
    #     print("Result:", task.result())


    async with asyncio.TaskGroup() as task_group:
        tasks = [task_group.create_task(endpoint(route)) for route in tests]
        print(await tasks[0])
        
    end = time.perf_counter()

    print(f"Time take: {end - start:.2f}s")




asyncio.run(server())
