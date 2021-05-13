# Python Speedtest

Python script to test your internet connection. Made for regular testing

## Getting Started

### Prerequisites

You will need Pyhton 3.7 (older version of Python may work but was not tested)

### Installing

Get the 2 sources files, [speedCheck.py](speedCheck.py) and [speedtest.py](speedtest.py).

In the Console navigate to the Folder where you saved the files and run:

```
python speedCheck.py
```
The results will be shown at the end in the Console and the detailled results will be saved by default in the files SpeedTestResults.txt and SpeedTestResultsLow.txt if the Speed is Low

To change the File Names, the line seperator and what is considered Low Download or Upload Speed open [speedCheck.py](speedCheck.py) in an editor and change lines [33](https://github.com/maxwai/Python-speedtest/blob/2e72f14643681be50e3582cdd7bc97e44d2e203d/speedCheck.py#L33) to [41](https://github.com/maxwai/Python-speedtest/blob/2e72f14643681be50e3582cdd7bc97e44d2e203d/speedCheck.py#L41)

## Deployment

This program is primarely meant for use at a server to be run at specific times for example to run it every 3 Hours in a NAS to test and log the Internet Speed at Home. For this pls see how to execute python files on your server

## Authors

* **Maximilian Waidelich** - *Initial work* - [maxwai](https://github.com/maxwai)

## License

This project is licensed under the GNU General Public License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* **Matt Martz** - *speedtest.py* - [speedtest-cli](https://pypi.org/project/speedtest-cli/)
* **Vladimir Ignatev** - *progress bar* - [progress.py](https://gist.github.com/vladignatyev/06860ec2040cb497f0f3)
