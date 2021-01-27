#!/usr/bin/env python
"""
Module runs local command across list of identified files

Uses defined parsing function that is passed as lambda from command line
"""
from plumbum import cli, local
from data_structures.parallel_iter import iter_threaded


class Pyrallel(cli.Application):
    """
    Run program in parallel over list of files, allotting various threads and distributing over
    a provided number of workers
    """
    program_string = str
    workers: int = 1
    threads_per_worker: int = 1

    @cli.switch(["-w", "--workers"], int, help="Number of workers, default 1")
    def get_workers(self, workers):
        """
        Set number of workers over which to distribute
        """
        if workers < 1:
            raise TypeError("Workers must be positive")
        self.workers = workers

    @cli.switch(["-t", "--threads-per-worker"], int, help="Number of threads to allow each worker to use")
    def get_threads(self, threads):
        """
        Set number of threads allowed for each worker
        """
        if threads < 1:
            raise TypeError("Threads must be positive")
        self.threads_per_worker = threads

    @cli.switch(["-p", "--program-string"], str, help="Quoted program string to be evaluated as f string")
    def get_program(self, program):
        """
        Set program string to modify
        """
        self.program_string = program

    @staticmethod
    def gather_files() -> list:
        """
        Gather input files from command line as input from user - meant to be used with cli iterator
        """
        data_files = []
        try:
            file = input()
            while True:
                data_files.append(file)
                file = input()
        except EOFError:
            pass
        return data_files

    # pylint: disable=arguments-differ
    def main(self):
        """
        Run command using provided number of threads
        """
        data_files = Pyrallel.gather_files()

        @iter_threaded(self.workers, file=data_files)
        def map_program(file):
            program_string = self.program_string.replace("{file}", file)\
                .replace("{threads}", str(self.threads_per_worker)).split()
            return local[program_string[0]][program_string[1:]]()

        for val in map_program(""):
            print(val)


if __name__ == "__main__":
    Pyrallel.run()
