/*
 *   NDS Roms Trimmer
 *
 *   Copyleft (C) 2008 by
 *   Fortunato Ventre - <vorione@gmail.com> - <http://www.voria.org>
 *
 *   'Trim' is free software; you can redistribute it and/or modify
 *   it under the terms of the GNU General Public License as published by
 *   the Free Software Foundation; either version 3 of the License, or
 *   (at your option) any later version.
 *
 *   This program is distributed in the hope that it will be useful,
 *   but WITHOUT ANY WARRANTY; without even the implied warranty of
 *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *   See the GNU General Public License for more details.
 *   <http://www.gnu.org/licenses/gpl.txt>
 *
 *   NDS File Format Specifications:
 *   <http://www.bottledlight.com/ds/index.php/FileFormats/NDSFormat>
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define VERSION "1.6.4"

/* 1 MB */
#define BUFSIZE 1048576

/* offsets */
#define ROMSIZE 0x80

struct rom_t
{
	unsigned int filesize; /* Untrimmed file size */
	char gametitle[13];
	unsigned int size; /* Trimmed file size, 4 bytes long */
};

/*
 * In WiFi enabled games, WiFi data is located on 136 bytes following rom data.
 * This information is not completely trusted (though all the roms i've tested
 * have given me no problems at all).
 * For minimizing the risk of faulty trims, we save a bit more bytes too.
 * I like number '256'. :p
 */
#define WIFIDATA 256

void usage(char *argv[])
{
	printf("Nintendo DS Roms Trimmer ");
	printf(VERSION);
	printf("\nCopyleft by\n");
	printf("Fortunato Ventre - vorione@gmail.com - http://www.voria.org\n\n");
	printf("USAGE: %s [OPTIONS] rom1 rom2 ...\n", argv[0]);
	printf("\nOPTIONS:\n");
	printf("  -b\t\tDo NOT preserve original rom(s) as backup.\n");
	printf("    \t\tThis option is only valid when the destination directory\n");
	printf("    \t\tis the same as the original one. Otherwise, it's ignored.\n");
	printf("  -d <dir>\tPut trimmed rom(s) in <dir> directory.\n");
	printf("  -h\t\tPrint this help.\n");
	printf("  -q\t\tDo not print rom statistics.\n");
	printf("  -s\t\tSimulate trim action. No real write will be performed.\n");
	printf("\nReleased under GPLv3 terms.\n");
}

/*
 * Transforms 'path' in an absolute path.
 * Returns a string (to be freed when done) holding absolute path; NULL on fail.
 */
char *abs_path(const char *path)
{

	char *cwd = NULL;
	char *result = NULL;

	cwd = getcwd(NULL, 0);
	if (chdir(path) != 0) {
		free(cwd);
		return NULL;
	}

	/* Get 'path' dir in absolute form and return to initial working dir */
	result = getcwd(NULL, 0);
	if (chdir(cwd) != 0) {
		fprintf(stderr, "ERROR: Unable to change back to original working directory!\n");
		free(cwd);
		exit(3);
	}

	free(cwd);
	return result;
}

/*
 * Cut out full path (if any) from 'path'.
 * Returns a string (to be freed when done) holding filename on success; NULL on fail.
 */
char *get_filename(const char *path)
{

	char *result = NULL;
	char *delpos = NULL; /* Pointer to position of the last path delimiter */

	delpos = strrchr(path, '/');

#ifdef _WINDOWS_
	if (delpos == NULL) {
		delpos = strrchr(path, '\\');
	}
#endif

	if (delpos == NULL) {
		if ((result = (char *) malloc(strlen(path) + 1)) != NULL) {
			strcpy(result, path);
		}
		return result;
	}

	if ((result = (char *) malloc(strlen(delpos) + 1)) != NULL) {
		strcpy(result, delpos + 1);
	}
	return result;
}

/*
 * Cut out filename from 'path'.
 * Returns a string (to be freed when done) holding absolute path extracted from 'path'.
 * Returns NULL on fail.
 */
char *get_path(const char *path)
{

	char *temp = NULL;
	char *result = NULL;
	char *delpos = NULL;
	int i;

	delpos = strrchr(path, '/');

#ifdef _WINDOWS_
	if (delpos == NULL) {
		delpos = strrchr(path, '\\');
	}
#endif

	if (delpos == NULL) {
		/* Delimiter not found, path only contains filename */
		result = getcwd(NULL, 0);
		return result;
	}

	i = strlen(path) - strlen(delpos);
	if ((temp = (char *) malloc(i + 1)) == NULL) {
		return NULL;
	}
	strncpy(temp, path, i);
	temp[i] = '\0';

	result = abs_path(temp);

	free(temp);
	return result;
}

int main(int argc, char *argv[])
{

	FILE *fin;
	FILE *fout;

	char *currentdir = NULL;
	char *outputdir = NULL;
	char *romdir = NULL;
	char *outputname = NULL;
	char *tempname = NULL;
	char *backupname = NULL;

	char buffer[BUFSIZE];
	unsigned int pos;      /* Actual position in input file. Used while copying data */
	unsigned int nextdata; /* Next data to copy */

	struct rom_t rom;

	int trimmedroms = 0;
	unsigned int savedspace = 0;

	/* Command line options flags */
	int nobackup = 0;
	int quiet = 0;
	int simulation = 0;

	int opt;
	int i;

	opterr = 0;

	while ((opt = getopt(argc, argv, "bd:hqs")) != -1) {
		switch (opt) {
		case 'b':
			nobackup = 1;
			break;
		case 'd':
			if ((outputdir = (char *) malloc(strlen(optarg))) == NULL) {
				fprintf(stderr, "ERROR: Can't allocate memory for output directory. Aborted.\n");
				exit(3);
			}
			strcpy(outputdir, optarg);
			break;
		case 'h':
			usage(argv);
			exit(2);
		case 'q':
			quiet = 1;
			break;
		case 's':
			simulation = 1;
			break;
		default:
			if (optopt == 'd') {
				fprintf(stderr, "Option '-d' requires an argument. ");
			} else {
				fprintf(stderr, "Unknown option '-%c' specified. ", optopt);
			}
			fprintf(stderr, "Use '-h' for help.\n");
			exit(1);
		}
	}

	if (argc == 1 || optind == argc) {
		fprintf(stderr, "No rom(s) specified. Use '-h' for help.\n");
		exit(1);
	}

	currentdir = getcwd(NULL, 0);

	/* Make sure that outputdir is in absolute form */
	if (outputdir != NULL) {                              /* outputdir specified on command line */
		if ((romdir = abs_path(outputdir)) == NULL) { /* romdir var used as temp var */
			fprintf(stderr, "ERROR: Can't get absolute path for '%s'. Aborted.\n", outputdir);
			exit(3);
		}
		free(outputdir);
		outputdir = romdir;
		romdir = NULL;
	} else { /* outputdir NOT specified on command line */
		outputdir = getcwd(NULL, 0);
	}

	/* Start main loop */
	for (i = optind; i < argc; i++) {
		/*
		 * Test if file is a NDS rom by extension.
		 * This is not the best way to do it, but I'm too lazy to implement a better check.
		 * It just works.
		 */
		if (strcasecmp(argv[i] + strlen(argv[i]) - 4, ".nds") != 0) {
			continue;
		}

		/* Get absolute path of rom directory */
		if ((romdir = get_path(argv[i])) == NULL) {
			fprintf(stderr, "ERROR: Can't get absolute path. Aborted.\n");
			exit(3);
		}

		/* Open input file */
		if ((fin = fopen(argv[i], "rb")) == NULL) {
			fprintf(stderr, "\tWARNING: Can't open input file for reading. Skipped.\n");
			free(romdir);
			romdir = NULL;
			continue;
		}

		/* Get game title */
		fread(&rom.gametitle, 12, 1, fin);
		rom.gametitle[12] = '\0';

		/* Get file size */
		fseek(fin, 0, SEEK_END);
		rom.filesize = ftell(fin);

		/* Read real size */
		fseek(fin, ROMSIZE, SEEK_SET);
		fread(&rom.size, 4, 1, fin);

		/* Get the output file name */
		if ((outputname = get_filename(argv[i])) == NULL) {
			fprintf(stderr, "ERROR: Cannot get the output file name for '%s'. Aborted.\n", argv[i]);
			exit(3);
		}

		printf("*****  %s (%s)\n", outputname, rom.gametitle);

		/*
		 * Some (few) roms do not respect NDS file format specifications.
		 * As result, the reading of rom size at offset 0x80 returns a 0 bytes size.
		 * We can't trim them.
		 */
		if (rom.size == 0) {
			fprintf(stderr, "\tWARNING: Not a standard rom. Skipped.\n");
			free(outputname);
			outputname = NULL;
			free(romdir);
			romdir = NULL;
			fclose(fin);
			continue;
		}

		/*
		 * Add WiFi data. It's useless to check for it to be
		 * or not to be removed, because it's a very low wasted space.
		 * So, we save it everytime.
		 */
		rom.size += WIFIDATA;

		/* Print stats */
		if (!quiet) {
			printf("\tOriginal Size:\t%6.d kB\n", rom.filesize / 1024);
			printf("\tTrimmed Size:\t%6.d kB\n", rom.size / 1024);
		}

		/* Check if trimmed rom size is greater than original size. This should never happen... */
		if (rom.filesize < rom.size) {
			fprintf(stderr, "\tWARNING: Strange things happened. Skipped.\n");
			free(outputname);
			outputname = NULL;
			free(romdir);
			romdir = NULL;
			fclose(fin);
			continue;
		}

		/* Check if trimming is really needed */
		if (rom.filesize == rom.size) {
			fprintf(stderr, "\tWARNING: No need to trim. Skipped.\n");
			free(outputname);
			outputname = NULL;
			free(romdir);
			romdir = NULL;
			fclose(fin);
			continue;
		}

		if (!quiet) {
			printf("\tSaved Space:\t%6.d kB\n", (rom.filesize - rom.size) / 1024);
		}

		/*
		 * If simulation is enabled, rom will not trimmed for real.
		 * We can skip to next one.
		 */
		if (simulation) {
			savedspace += rom.filesize - rom.size;
			trimmedroms++;
			free(outputname);
			outputname = NULL;
			free(romdir);
			romdir = NULL;
			fclose(fin);
			continue;
		}

		/* Prepare temp name */
		if ((tempname = (char *) malloc(strlen(outputname) + 9)) == NULL) {
			fprintf(stderr, "\tWARNING: Can't allocate memory for temp name. Skipped.\n");
			free(outputname);
			outputname = NULL;
			free(romdir);
			romdir = NULL;
			continue;
		}
		strcpy(tempname, outputname);
		strcat(tempname, ".trimmed");

		/* Change to output directory */
		if (chdir(outputdir) != 0) {
			fprintf(stderr, "ERROR: Can't change to output directory. Aborted.\n");
			exit(3);
		}

		/* Open temp file */
		if ((fout = fopen(tempname, "wb")) == NULL) {
			fprintf(stderr, "\tWARNING: Can't open output file for writing. Skipped.\n");
			free(tempname);
			tempname = NULL;
			free(outputname);
			outputname = NULL;
			free(romdir);
			romdir = NULL;
			fclose(fin);
			continue;
		}

		/* Rewind input file and start to copy */
		rewind(fin);

		pos = 0;
		nextdata = BUFSIZE;

		while (pos < rom.size) {
			if (pos + BUFSIZE > rom.size) {
				nextdata = rom.size - pos;
			}
			fread(&buffer, nextdata, 1, fin);
			fwrite(&buffer, nextdata, 1, fout);
			pos += nextdata;
		}

		fclose(fout);
		fclose(fin);

		savedspace += rom.filesize - rom.size;
		trimmedroms++;

		if (strcmp(outputdir, romdir) == 0) {
			if (nobackup) {
				if (remove(outputname) == 0) {
					if (rename(tempname, outputname) != 0) {
						fprintf(stderr, "\tWARNING: Unable to rename trimmed file. ");
						fprintf(stderr, "It has '.trimmed' extension.\n");
					}
				} else {
					fprintf(stderr, "\tWARNING: Unable to delete original file. ");
					fprintf(stderr, "Trimmed file has '.trimmed' extension.\n");
				}
			} else {
				/* Prepare backup name */
				if ((backupname = (char *) malloc(strlen(outputname) + 5)) == NULL) {
					fprintf(stderr, "\tWARNING: Can't allocate memory for backup name. ");
					fprintf(stderr, "Trimmed file has '.trimmed' extension.\n");
					free(tempname);
					tempname = NULL;
					free(outputname);
					outputname = NULL;
					free(romdir);
					romdir = NULL;
					continue;
				}
				strcpy(backupname, outputname);
				strcat(backupname, ".bak");

				if (rename(outputname, backupname) == 0) {
					if (rename(tempname, outputname) != 0) {
						fprintf(stderr, "\tWARNING: Unable to rename trimmed file. ");
						fprintf(stderr, "It has '.trimmed' extension.\n");
					}
				} else {
					fprintf(stderr, "\tWARNING: Unable to rename original file. ");
					fprintf(stderr, "Trimmed file has '.trimmed' extension.\n");
				}
				free(backupname);
				backupname = NULL;
			}
		} else { /* outputdir != romdir */
			if (rename(tempname, outputname) != 0) {
				fprintf(stderr, "\tWARNING: Unable to rename trimmed file. ");
				fprintf(stderr, "It has '.trimmed' extension.\n");
			}
		}

		free(tempname);
		tempname = NULL;
		free(outputname);
		outputname = NULL;
		free(romdir);
		romdir = NULL;

		/* Change back to currentdir */
		if (chdir(currentdir) != 0) {
			fprintf(stderr, "ERROR: Can't change back to original working directory. Aborted.\n");
			exit(3);
		}
	}
	/* End main loop */

	free(currentdir);
	free(outputdir);

	if (trimmedroms > 0) {
		if (simulation) {
			printf("\nSimulation performed on %d rom(s). ", trimmedroms);
			printf("A trim can save: %d kB\n", savedspace / 1024);
		} else {
			printf("\n%d rom(s) trimmed. ", trimmedroms);
			printf("Total saved space: %d kB\n", savedspace / 1024);
		}
	} else {
		printf("Nothing done.\n");
	}

	return 0;
}
