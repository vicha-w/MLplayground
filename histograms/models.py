import os.path
import json
import logging
import pandas as pd  # https://betterprogramming.pub/3-techniques-for-importing-large-csv-files-into-a-django-app-2b6e5e47dba0
from django.db import models
from django.contrib.postgres.fields import ArrayField
from runs.models import Run
from lumisections.models import Lumisection
from histogram_file_manager.models import HistogramDataFile

logger = logging.getLogger(__name__)

# Specifies the number of lines that the csv file will be
# chunked into during parsing 2D histograms.
# E.g. 50 means that a 120-line csv will be read in two 50-line chunks
# and one 20-line chunk.
LUMISECTION_HISTOGRAM_2D_CHUNK_SIZE = 50


class HistogramBase(models.Model):
    """
    Base model to be inherited from Run and Lumisection Histograms
    """
    date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=220)
    source_data_file = models.ForeignKey(
        HistogramDataFile,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        help_text=
        "Source data file that the specific Histogram was read from, if any",
    )


class RunHistogram(HistogramBase):
    run = models.ForeignKey(Run, on_delete=models.CASCADE)
    primary_dataset = models.CharField(max_length=220)
    path = models.CharField(max_length=220)
    entries = models.BigIntegerField(null=True)
    mean = models.FloatField(null=True)
    rms = models.FloatField(null=True)
    skewness = models.FloatField(null=True)
    kurtosis = models.FloatField(null=True)

    def __str__(self):
        return f"run: {self.run.run_number} / dataset: {self.primary_dataset} / histo: {self.title}"

    # TODO
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=['run', 'primary_dataset', 'title'],
    #             name='unique run/dataset/histogram combination')
    #     ]


class LumisectionHistogramBase(models.Model):
    """
    Abstract Base model that both 1D and 2D lumisection histograms inherit from.
    
    """
    lumisection = models.ForeignKey(Lumisection, on_delete=models.CASCADE)

    entries = models.IntegerField(blank=True, null=True)

    class Meta:
        abstract = True


class LumisectionHistogram1D(HistogramBase, LumisectionHistogramBase):

    data = ArrayField(models.FloatField(), blank=True)
    x_min = models.FloatField(blank=True, null=True)
    x_max = models.FloatField(blank=True, null=True)
    x_bin = models.IntegerField(blank=True, null=True)

    @staticmethod
    def from_csv(file_path, data_era: str = ""):
        """
        Import 1D Lumisection Histograms from a csv file
        """
        df = pd.read_csv(file_path)
        logger.debug(f"Datafile head: {df.head()}")
        # logger.debug(f"Datafile columns:\n {df.columns}")

        # Create an entry for a new data file in the database
        histogram_data_file, created = HistogramDataFile.objects.get_or_create(
            filepath=file_path,
            data_dimensionality=HistogramDataFile.DIMENSIONALITY_1D,
            data_era=data_era,
            granularity=HistogramDataFile.GRANULARITY_LUMISECTION)

        file_size = os.path.getsize(file_path)
        file_line_count = 0  # Total lines in CSV

        # Get number of lines, this may take a "long" time, but
        # it's needed to record our progress while parsing the file
        with open(file_path, 'r') as fp:
            for file_line_count, line in enumerate(fp):
                pass

        if not created and histogram_data_file.filesize != file_size:
            logger.warning(
                f"File '{file_path}' already in DB but size differs! "
                f"({histogram_data_file.filesize} bytes in DB, "
                f"{file_size} bytes actually)")

        # Update file size anyway
        histogram_data_file.filesize = file_size
        histogram_data_file.entries_total = file_line_count
        histogram_data_file.save()

        lumisection_histos1D = []  # New LumisectionHisto1D entries
        count = 0

        for index, row in df.iterrows():
            run_number = row["fromrun"]
            lumi_number = row["fromlumi"]
            title = row["hname"]
            entries = row["entries"]
            data = json.loads(row["histo"])

            logger.debug(
                f"Run: {run_number}\tLumisection: {lumi_number}\tTitle: {title}"
            )

            # Get existing or create new Run entry
            run, _ = Run.objects.get_or_create(run_number=run_number)

            # Get existing or create new Lumisection entry
            lumisection, _ = Lumisection.objects.get_or_create(
                run=run, ls_number=lumi_number)

            lumisection_histo1D = LumisectionHistogram1D(
                lumisection=lumisection,
                title=title,
                entries=entries,
                data=data,
                source_data_file=histogram_data_file)

            # lumisection_histos1D.append(lumisection_histo1D)
            lumisection_histo1D.save()
            count += 1
            histogram_data_file.entries_processed += 1
            histogram_data_file.save()

            # Bulk create every 50 entries
            # if count == 50:

            # LumisectionHistogram1D.objects.bulk_create(
            #     lumisection_histos1D, ignore_conflicts=True)
            # logger.info(
            #     "50 lumisections 1D histograms successfully added!")
            # histogram_data_file.entries_processed += 50
            # histogram_data_file.save()
            # count = 0
            # lumisection_histos1D = []

        # if lumisection_histos1D:  # If total entries not a multiple of 50, some will be left
        #     LumisectionHistogram1D.objects.bulk_create(lumisection_histos1D,
        #                                                ignore_conflicts=True)
        #     histogram_data_file.entries_processed += len(lumisection_histos1D)
        #     histogram_data_file.save()

    def __str__(self):
        return f"run {self.lumisection.run.run_number} / lumisection {self.lumisection.ls_number} / name {self.title}"

    # TODO
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["lumisection", "HistogramBase.title"],
    #             name="unique run / ls / 1d histogram combination",
    #         )
    #     ]


def get_last_chunk(histogram_data_file, chunk_size):
    """
    Function that calculates the last chunk that was parsed from
    a 2D Lumisection histogram csv file.
    """
    return int(histogram_data_file.entries_processed / chunk_size)


class LumisectionHistogram2D(HistogramBase, LumisectionHistogramBase):
    """
    Model containing 2D Lumisection Histogram information
    """
    data = ArrayField(models.FloatField(), blank=True)
    # ArrayField( ArrayField( models.IntegerField(blank=True), size=XX, ), size=XX,)
    x_min = models.FloatField(blank=True, null=True)
    x_max = models.FloatField(blank=True, null=True)
    x_bin = models.IntegerField(blank=True, null=True)
    y_max = models.FloatField(blank=True, null=True)
    y_min = models.FloatField(blank=True, null=True)
    y_bin = models.IntegerField(blank=True, null=True)

    @staticmethod
    def from_csv(file_path, data_era: str = "", resume: bool = True):
        """
        Import 2D Lumisection Histograms from a csv file
        
        Parameters:
        - file_path: A path to a .csv file containing a 2D Lumisection Histogram
        - data_era: The era that the data refers to (e.g. 2018A)
        - resume: Specify whether 
        """
        logger.info(
            f"Importing 2D Lumisection Histograms from '{file_path}', "
            f"splitting into chunks of {LUMISECTION_HISTOGRAM_2D_CHUNK_SIZE}")

        # Create an entry for a new data file in the database
        histogram_data_file, created = HistogramDataFile.objects.get_or_create(
            filepath=file_path,
            data_dimensionality=HistogramDataFile.DIMENSIONALITY_2D,
            data_era=data_era,
            granularity=HistogramDataFile.GRANULARITY_LUMISECTION,
        )

        file_size = os.path.getsize(file_path)
        file_line_count = 0  # Total lines in CSV

        # Get number of lines, this may take a "long" time, but
        # it's needed to record our progress while parsing the file
        with open(file_path, 'r') as fp:
            for file_line_count, line in enumerate(fp):
                pass

        # Histogram file was already recorded in database
        if not created and histogram_data_file.filesize != file_size:
            logger.warning(
                f"File '{file_path}' already in DB but size differs! "
                f"({histogram_data_file.filesize} bytes in DB, "
                f"{file_size} bytes actually)")

        # Update file size anyway
        histogram_data_file.filesize = file_size
        histogram_data_file.entries_total = file_line_count
        histogram_data_file.save()

        # Last saved chunk in DB.
        last_chunk = 0 if created else get_last_chunk(
            histogram_data_file,
            LUMISECTION_HISTOGRAM_2D_CHUNK_SIZE) if resume else 0

        logger.info(f"Last chunk: {last_chunk}")
        # Keep track of current chunk
        current_chunk = 0
        # Keep track of lines read
        num_lines_read = 0
        reader = pd.read_csv(file_path,
                             chunksize=LUMISECTION_HISTOGRAM_2D_CHUNK_SIZE)
        logger.info(f"File has {file_line_count} lines")
        for df in reader:
            if resume and current_chunk < last_chunk:
                logger.debug(f"Skipping chunk {current_chunk}")
                current_chunk += 1
                continue
            else:
                logger.debug(f"Reading chunk {current_chunk}")

            # For each line in chunk
            for index, row in df.iterrows():
                run_number = row["fromrun"]
                lumi_number = row["fromlumi"]
                title = row["hname"]
                entries = row["entries"]
                data = json.loads(row["histo"])
                logger.debug(
                    f"Run: {run_number}\tLumisection: {lumi_number}\tTitle: {title}"
                )

                run, _ = Run.objects.get_or_create(run_number=run_number)
                lumisection, _ = Lumisection.objects.get_or_create(
                    run=run, ls_number=lumi_number)

                lumisection_histo2D = LumisectionHistogram2D(
                    lumisection=lumisection,
                    title=title,
                    entries=entries,
                    data=data,
                    source_data_file=histogram_data_file)

                lumisection_histo2D.save()
                num_lines_read += 1
                histogram_data_file.entries_processed += 1
                histogram_data_file.save()

            # Does not work with multi-table inheritance
            # LumisectionHistogram2D.objects.bulk_create(lumisection_histos2D,
            # ignore_conflicts=True)

            logger.info(
                f"{num_lines_read} x "
                f"2D lumisection histos successfully added from chunk {current_chunk}!"
            )
            # num_lines_read += len(lumisection_histos2D)
            current_chunk += 1
            num_lines_read = 0  # Reset num lines read from chunk
            # Record progress in DB
            # Not safe to assume progress by chunks read,
            # the last chunk may have less lines than expected
            # histogram_data_file.entries_processed = num_lines_read
            # histogram_data_file.save()  # Save entries and move to next chunk

    def __str__(self):
        return f"run {self.lumisection.run.run_number} / lumisection {self.lumisection.ls_number} / name {self.title}"

    # TODO
    # class Meta:
    #     constraints = [
    #         models.UniqueConstraint(
    #             fields=["lumisection", "title"],
    #             name="unique run / ls / 2d histogram combination",
    #         )
    #     ]
