# Test-Repo-AA7710
Starting a test repo to see how comfortable I am with Git. 

This repo has a total of 5 files:

DeviceConfig_v2.py: The code that configures the device class, dataclasses amongst other device specific info. It also has the regex patterns for the specific outputs we are looking to match for an individual device.

SpBConfig_v2.py: The code is a customized version of the original Cirrus Link MQTT implementation. Specific instances of two devices are created to handle, payloag generation, and publishing onto a prespecified MQTT client.

genPayload.py: The helper function to generate the payload, that has device parameters and MQTT client logistics supplied to it externally.

sparkplug_b.py & sparkplug_b_pb2.py: The libraries that need to be within the root directory from where the script is being executed.

Date Updated: August 19, 2022, Anand Agrawal
