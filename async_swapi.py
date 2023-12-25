import asyncio
import datetime
from aiohttp import ClientSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from more_itertools import chunked

from models import Base, Character
from url import URL
import async_swapi_tech

PG_DSN = 'postgresql+asyncpg:://postgres:postgres@localhost:5431/async'
engine = create_async_engine(PG_DSN)
Session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

CHUNK_SIZE = 82


async def chunked_async(async_iter, size):

    buffer = []
    while True:
        try:
            item = await async_iter.__anext__()
        except StopAsyncIteration:
            break
        buffer.append(item)
        if len(buffer) == size:
            yield buffer
            buffer = []


async def res_to_data(json_res):
    return {'name': json_res.get('name'),
            'birth_year': json_res['birth_year'],
            'gender': json_res['gender'],
            'height': json_res['height'],
            'mass': json_res['mass'],
            'eye_color': json_res['eye_color'],
            'hair_color': json_res['hair_color'],
            'skin_color': json_res['skin_color']}


async def get_extra_fields(url_list, session):
    name_list = []
    for url in url_list:
        async with session.get(url) as response:
            json_res = await response.json()
            name_list.append(json_res['name'])
    return ', '.join(name_list)


async def get_films(url_list, session):
    name_list = []
    for url in url_list:
        async with session.get(url) as response:
            json_res = await response.json()
            name_list.append(json_res['title'])
    return ', '.join(name_list)


async def get_person(people_id: int, session: ClientSession):
    print(f'begin {people_id}')
    async with session.get(f'{URL}api/people/{people_id}') as response:
        json_res = await response.json()
        if json_res.get('detail', False):
            return {'id': people_id,
                    'name': 'n/a',
                    'birth_year': 'n/a',
                    'gender': 'n/a',
                    'height': 'n/a',
                    'mass': 'n/a',
                    'eye_color': 'n/a',
                    'hair_color': 'n/a',
                    'skin_color': 'n/a',
                    'films': 'n/a',
                    'homeworld': 'n/a',
                    'species': 'n/a',
                    'starships': 'n/a',
                    'vehicles': 'n/a',
                    }
        json_data = await res_to_data(json_res)
        json_data['id'] = people_id
        json_data['films'] = await get_films(json_res['films'], session)
        json_data['homeworld'] = await get_extra_fields([json_res['homeworld']], session)
        json_data['species'] = await get_extra_fields(json_res['species'], session)
        json_data['starships'] = await get_extra_fields(json_res['starships'], session)
        json_data['vehicles'] = await get_extra_fields(json_res['vehicles'], session)
    print(f'end {people_id}')
    return json_data


async def get_people():
    async with ClientSession() as session:
        for chunk in chunked(range(1, 83), CHUNK_SIZE):
            coroutines = [get_person(people_id=i, session=session)
                          for i in chunk]
            results = await asyncio.gather(*coroutines)
            for item in results:
                yield item


async def insert_people(people_chunk):
    async with Session() as session:
        session.add_all([Character(**item) for item in people_chunk])
        await session.commit()


async def main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    async for chunk in chunked_async(get_people(), CHUNK_SIZE):
        asyncio.create_task(insert_people(chunk))

    tasks = set(asyncio.all_tasks()) - {asyncio.current_task()}
    for task in tasks:
        await task


start = datetime.datetime.now()
# asyncio.run(main())
if URL:
    asyncio.run(main())
else:
    asyncio.run(async_swapi_tech.main())
print(datetime.datetime.now() - start)
