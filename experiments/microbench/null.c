#include <sys/types.h>
#include <unistd.h>
#include <stdlib.h>
#include <stdio.h>
#include <sys/time.h>

#define SEC_USEC 1000000

void create_children(int count)
{
    for (int i = 0; i < count; i++)
    {
        if (!fork())
            exit(0);
    }
}

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        exit(-1);
    }

    int count = atoi(argv[1]);

    struct timeval t[2];

    gettimeofday(&t[0], NULL);
    create_children(count);
    gettimeofday(&t[1], NULL);

    unsigned long long diff = (t[1].tv_sec * SEC_USEC + t[1].tv_usec) -
        (t[0].tv_sec * SEC_USEC + t[0].tv_usec);
    fprintf(stderr, "%d %llu\n", count, diff);

    return 0;
}
