#include <stdio.h>
#include <string.h>
#include <mpi.h>
#include <netcdf.h>
#include <netcdf_par.h>
#include <netcdf_filter.h>

int main(int argc, char **argv) {
    int ncid, status;
    printf("netCDF-C: %s\n", nc_inq_libvers()); fflush(stdout);
    if (argc > 1 && !strcmp(argv[1], "filter")) {
        int dimid, varid;
        status = nc_create("native-filter.nc", NC_NETCDF4 | NC_CLOBBER, &ncid);
        if (status) return 2;
        nc_def_dim(ncid, "n", 4, &dimid);
        nc_def_var(ncid, "data", NC_DOUBLE, 1, &dimid, &varid);
        status = nc_def_var_zstandard(ncid, varid, 4);
        printf("native zstd status=%d %s\n", status, nc_strerror(status));
        nc_close(ncid);
        return status ? 1 : 0;
    }
    MPI_Init(&argc, &argv);
    int rank, sum, one = 1;
    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    status = MPI_Allreduce(&one, &sum, 1, MPI_INT, MPI_SUM, MPI_COMM_WORLD);
    printf("rank=%d MPI_Allreduce status=%d sum=%d; entering nc_create_par\n", rank, status, sum); fflush(stdout);
    status = nc_create_par("native-parallel.nc", NC_NETCDF4 | NC_CLASSIC_MODEL | NC_CLOBBER,
                           MPI_COMM_WORLD, MPI_INFO_NULL, &ncid);
    printf("rank=%d nc_create_par status=%d %s\n", rank, status, nc_strerror(status)); fflush(stdout);
    if (!status) nc_close(ncid);
    MPI_Finalize();
    return status ? 1 : 0;
}
