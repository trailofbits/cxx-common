set(LIBRARY_ROOT "${CXX_COMMON_REPOSITORY_ROOT}/capstone")

set(CAPSTONE_FOUND TRUE)
set(CAPSTONE_INCLUDE_DIRS "${LIBRARY_ROOT}/include")

set(CAPSTONE_LIBRARIES
    ${LIBRARY_ROOT}/lib/libcapstone.a
)

mark_as_advanced(FORCE CAPSTONE_FOUND)
mark_as_advanced(FORCE CAPSTONE_INCLUDE_DIRS)
mark_as_advanced(FORCE CAPSTONE_LIBRARIES)
