#include <unistd.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        exit(-1);
    }

    int count = atoi(argv[1]);

    for (int i = 0; i < count; i++)
    {
        close(999);
    }

    return 0;
}
