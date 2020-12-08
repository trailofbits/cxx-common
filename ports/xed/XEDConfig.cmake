FUNCTION(SET_LIBRARY_TARGET NAMESPACE LIB_NAME LINK_TYPE DEBUG_LIB_FILE_NAME RELEASE_LIB_FILE_NAME INCLUDE_DIR)
    ADD_LIBRARY(${NAMESPACE}::${LIB_NAME} ${LINK_TYPE} IMPORTED)
    SET_TARGET_PROPERTIES(${NAMESPACE}::${LIB_NAME} PROPERTIES
                          IMPORTED_CONFIGURATIONS "RELEASE;DEBUG"
                          IMPORTED_LOCATION_RELEASE "${RELEASE_LIB_FILE_NAME}"
                          IMPORTED_LOCATION_DEBUG "${DEBUG_LIB_FILE_NAME}"
                          INTERFACE_INCLUDE_DIRECTORIES "${INCLUDE_DIR}"
                          )
    SET(${NAMESPACE}_${LIB_NAME}_FOUND 1)
ENDFUNCTION()

GET_FILENAME_COMPONENT(ROOT "${CMAKE_CURRENT_LIST_FILE}" PATH)
GET_FILENAME_COMPONENT(ROOT "${ROOT}" PATH)
GET_FILENAME_COMPONENT(ROOT "${ROOT}" PATH)

set(XED_STATIC_DEBUG_LIB "${ROOT}/debug/lib/libxed${CMAKE_STATIC_LIBRARY_SUFFIX}")
set(XED_SHARE_DEBUG_LIB "${ROOT}/debug/lib/libxed${CMAKE_SHARED_LIBRARY_SUFFIX}")
set(ILD_STATIC_DEBUG_LIB "${ROOT}/debug/lib/libxed-ild${CMAKE_STATIC_LIBRARY_SUFFIX}")
set(ILD_SHARE_DEBUG_LIB "${ROOT}/debug/lib/libxed-ild${CMAKE_SHARED_LIBRARY_SUFFIX}")

set(XED_STATIC_RELEASE_LIB "${ROOT}/lib/libxed${CMAKE_STATIC_LIBRARY_SUFFIX}")
set(XED_SHARE_RELEASE_LIB "${ROOT}/lib/libxed${CMAKE_SHARED_LIBRARY_SUFFIX}")
set(ILD_STATIC_RELEASE_LIB "${ROOT}/lib/libxed-ild${CMAKE_STATIC_LIBRARY_SUFFIX}")
set(ILD_SHARE_RELEASE_LIB "${ROOT}/lib/libxed-ild${CMAKE_SHARED_LIBRARY_SUFFIX}")

# Check for existence of debug libs
if (NOT EXISTS "${XED_STATIC_DEBUG_LIB}")
    set(XED_STATIC_DEBUG_LIB "${XED_STATIC_RELEASE_LIB}")
endif()
if (NOT EXISTS "${ILD_STATIC_DEBUG_LIB}")
    set(ILD_STATIC_DEBUG_LIB "${ILD_STATIC_RELEASE_LIB}")
endif()

# Check for existence of release libs
if (NOT EXISTS "${XED_STATIC_RELEASE_LIB}")
    set(XED_STATIC_RELEASE_LIB "${XED_STATIC_DEBUG_LIB}")
endif()
if (NOT EXISTS "${ILD_STATIC_RELEASE_LIB}")
    set(ILD_STATIC_RELEASE_LIB "${ILD_STATIC_DEBUG_LIB}")
endif()

SET_LIBRARY_TARGET("XED" "XED" "STATIC" "${XED_STATIC_DEBUG_LIB}" "${XED_STATIC_RELEASE_LIB}" "${ROOT}/include/xed")
SET_LIBRARY_TARGET("ILD" "XED" "STATIC" "${ILD_STATIC_DEBUG_LIB}" "${ILD_STATIC_RELEASE_LIB}" "${ROOT}/include/xed")