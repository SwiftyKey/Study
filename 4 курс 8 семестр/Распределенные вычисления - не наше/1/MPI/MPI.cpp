#include <mpi.h>
#include <iostream>

int main(int argc, char** argv) {
    int rank, size;
    MPI_Status status;
    short message = 0;

    MPI_Init(&argc, &argv);
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);

    if (size == 1) {
        std::cout << "[0] : single process, message = 0" << std::endl;
        MPI_Finalize();
        return 0;
    }

    int dest = (rank + 1) % size;
    int source = (rank - 1 + size) % size;

    if (rank == 0) {
        MPI_Send(&message, 1, MPI_SHORT, dest, 0, MPI_COMM_WORLD);

        MPI_Recv(&message, 1, MPI_SHORT, source, 0, MPI_COMM_WORLD, &status);
        std::cout << "[" << rank << "] : " << "recieve message '" << message << "'" << std::endl;
    }
    else {
        MPI_Recv(&message, 1, MPI_SHORT, source, 0, MPI_COMM_WORLD, &status);
        std::cout << "[" << rank << "] : " << "recieve message '" << message << "'" << std::endl;

        message++;
        MPI_Send(&message, 1, MPI_SHORT, dest, 0, MPI_COMM_WORLD);
    }

    MPI_Finalize();

    return 0;
}