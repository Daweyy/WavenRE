# WavenRE
Tool to **extract and translate game datas** from **[Waven](https://www.waven-game.com)** (from [Ankama Games](https://www.ankama.com)).

Power the [WavenData repository](https://github.com/Daweyy/WavenData) that help you track changes within the game and provide datas for related community projects.

### Usage :
Place following files from your game folder (in `Waven_Data/StreamingAssets/AssetBundles/core`) to the `/input` folder of this project :
- `data`
- `localization.de-de`
- `localization.en-us`
- `localization.es-es`
- `localization.fr-fr`
- `localization.pt-br`


Run with [Podman](https://podman.io)/[Docker](https://www.docker.com) :
```bash
podman compose up
# OR
docker compose up
```
*Feel free to run directly with Python, no support provided.*

Extracted datas will be found in `/output`.

Thanks [UnityPy module](https://github.com/K0lb3/UnityPy) & [Souff](https://github.com/souff).
