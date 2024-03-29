import os
import time
from tqdm import tqdm


class Mesh:
    """
    Reads all models/textures from the resources/models folder and creates corresponding GPU assets for them.
    (vao, textures) which can then be loaded into a "model" instance using their folder names.
    """
    _instance = None

    @classmethod
    def instance(cls, ctx=None) -> object:
        """
        Returns the singleton instance of the Mesh class, or creates a new one if it does not already exist.
        :param ctx: Context instance.
        :return: Singleton instance of the Mesh class.
        """
        if cls._instance is None and ctx is not None:
            cls._instance = cls(ctx)
        return cls._instance

    def __init__(self, app) -> None:
        """
        Constructor.
        :param app: Glw app.
        """
        if Mesh._instance is not None:
            raise RuntimeError("Mesh is a singleton and should not be instantiated more than once")

        self.app = app
        self.data = {}

        start = time.time()
        models_path = os.path.join(os.path.dirname(__file__), '../../resources/models')

        for root, dirs, files in (pbar := tqdm(os.walk(models_path), bar_format="{desc}")):
            name = os.path.basename(root)
            if name == "models":
                continue
            for filename in files:
                if os.path.splitext(filename)[1] in ['.gltf', '.glb']:
                    pbar.set_description(f"\033[32mLoading Model: {filename}\033[0m")
                    model_file_path = os.path.normpath(os.path.join(root, filename))
                    self.data[name] = self.app.loader.from_file(model_file_path)
        end = time.time()

        print("elapsed??: ", end - start)
