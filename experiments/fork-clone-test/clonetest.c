# include <stdio.h>
#include <sys/types.h>
#include <unistd.h>

int main(int argc, char **argv)
{
    pid_t the_pid = fork();

    if (!the_pid)
        printf("parent\n");
    else
        printf("child\n");

    return 0;
}
