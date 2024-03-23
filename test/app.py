import os

import imagecropper
import argparse

imagecropper.app.ApplicationCLI.run(argparse.Namespace(**{
    "configuration": "./debug.configuration.json",
}))

