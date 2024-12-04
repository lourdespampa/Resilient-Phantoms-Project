import pytest
import service.itunes as itunes

@pytest.mark.asyncio
async def test_service():
    artist = itunes.get_artist("The Beatles", 3)
    desc = str(artist)
    assert len(desc) > 0


