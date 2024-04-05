cmake_minimum_required(VERSION 3.16)

# !!!!!!!!!!!!!!!!!!!!!!!
# !!! Addon utilities !!!
# !!!!!!!!!!!!!!!!!!!!!!!

# * = all in src folder
set(USE_ADDONS "*" CACHE STRING "List of addons to use (git urls)")
set(CMAKE_DISABLE_SOURCE_CHANGES  ON)

message(STATUS "Using addons: ${USE_ADDONS}")

macro(pa_new addon)
    set(addon_name ${addon})
    set(${addon}_MODE patch CACHE STRING "Mode says how addon should be added.")

    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!
    set(${addon}_SOURCE_FILES PARENT_SCOPE)
    set(${addon}_INCLUDE_DIRS PARENT_SCOPE)
    set(${addon}_LIBRARIES    PARENT_SCOPE)
    set(${addon}_ADDONS       PARENT_SCOPE)

    if(NOT( ${addon} STREQUAL "Core"))
        set(${addon}_ADDONS ${${addon}_ADDONS} Core PARENT_SCOPE)
    endif()

    set(AVAILABLE_ADDONS ${AVAILABLE_ADDONS} ${addon} PARENT_SCOPE)
#    IF(${addon}_MODE STREQUAL "static")
#        add_library(${addon} STATIC ${SOURCE_FILES} ${HEADER_FILES})
#        link_libraries(${addon} ${LIBRARIES})
#        include_directories(${addon} ${INCLUDE_DIRS} ..)
#    ENDIF()
endmacro()

macro(pa_add_source_files source)
    list(APPEND ${addon_name}_SOURCE_FILES ${ARGV})
    list(APPEND ${addon_name}_HEADER_FILES ${ARGV})

    list(FILTER ${addon_name}_SOURCE_FILES EXCLUDE REGEX "h$")
    list(FILTER ${addon_name}_HEADER_FILES EXCLUDE REGEX "cpp$")
    list(FILTER ${addon_name}_HEADER_FILES EXCLUDE REGEX "c$")

    set(${addon_name}_SOURCE_FILES ${${addon_name}_SOURCE_FILES} PARENT_SCOPE)
    set(${addon_name}_HEADER_FILES ${${addon_name}_HEADER_FILES} PARENT_SCOPE)
endmacro()

macro(pa_include_directories directories)
    set(${addon_name}_INCLUDE_DIRS ${${addon_name}_INCLUDE_DIRS} ${ARGV} PARENT_SCOPE)
endmacro()

macro(pa_link_libraries libraries)
    set(${addon_name}_LIBRARIES ${${addon_name}_LIBRARIES} ${ARGV} PARENT_SCOPE)
endmacro()

macro(pa_require_addons addons)
    set(${addon_name}_ADDONS ${${addon_name}_ADDONS} ${ARGV} PARENT_SCOPE)
endmacro()

macro(load_addon addon)
    foreach(dependency ${${addon}_ADDONS})
        load_addon(${dependency})
    endforeach()

    LIST(APPEND ADDONS ${addon})
    LIST(REMOVE_DUPLICATES ADDONS)
endmacro()

macro(load_addons)
    SET(ADDONS)

    if(USE_ADDONS STREQUAL "*")
        set(USE_ADDONS ${AVAILABLE_ADDONS})
    endif()

    foreach(addon ${USE_ADDONS})
        load_addon(${addon})
    endforeach()
endmacro()

project(PetrolEngine)

set(SOURCE_FILES)
set(HEADER_FILES)
set(INCLUDE_DIRS)
set(STATIC_LIBS )

# install and build directories

find_package (Python COMPONENTS Interpreter Development)

execute_process(COMMAND ${Python_EXECUTABLE} ${CMAKE_CURRENT_SOURCE_DIR}/install.py ${USE_ADDONS} COMMAND_ECHO STDOUT)

FILE(GLOB __SRC__ src/*)
FOREACH(dir ${__SRC__})
  IF(IS_DIRECTORY ${dir})
    ADD_SUBDIRECTORY(${dir})
  ENDIF()
ENDFOREACH()

LOAD_ADDONS()
message(STATUS ${ADDONS})

foreach(ADDON ${ADDONS})
    message(STATUS "Adding: ${ADDON}")
    
    message(STATUS "  Source:")
    foreach(file ${${ADDON}_SOURCE_FILES})
        message(STATUS "    - ${file}")
    endforeach()

    message(STATUS "  Headers:")
    foreach(file ${${ADDON}_HEADER_FILES})
        message(STATUS "    - ${file}")
    endforeach()

    message(STATUS "  Include:")
    foreach(dir ${${ADDON}_INCLUDE_DIRS})
        message(STATUS "    - ${dir}")
    endforeach()

    list(APPEND HEADER_FILES ${${ADDON}_HEADER_FILES})
    list(APPEND INCLUDE_DIRS ${${ADDON}_INCLUDE_DIRS})
    IF(${${ADDON}_MODE} STREQUAL "patch")
        list(APPEND SOURCE_FILES ${${ADDON}_SOURCE_FILES})
        list(APPEND STATIC_LIBS ${${ADDON}_LIBRARIES})
        list(FILTER STATIC_LIBS EXCLUDE REGEX "PRIVATE")
    ELSEIF(${${ADDON}_MODE} STREQUAL "static")
        # TODO: Add static library support
        list(APPEND STATIC_LIBS ${ADDON})
    ENDIF()
endforeach()

set_property(GLOBAL PROPERTY ATTRIBUTES_PY "${CMAKE_CURRENT_SOURCE_DIR}/attributes.py")

function(implement_attributes projectt)
    get_target_property(target_type ${projectt} TYPE)
    if (NOT target_type STREQUAL "EXECUTABLE")
        return()
    endif ()
    get_target_property(headers ${projectt} SOURCES)
    list(FILTER headers INCLUDE REGEX ".h$")
    file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/attrsInclude)
    get_property(ATTRIBUTES_PY GLOBAL PROPERTY ATTRIBUTES_PY)
    get_target_property(includeDirs ${projectt} INCLUDE_DIRECTORIES)

    foreach(dir ${includeDirs})
        File(GLOB_RECURSE CHEAD ${dir}/*.h)
        list(APPEND headers ${CHEAD})
    endforeach()

    find_package (Python COMPONENTS Interpreter Development)
    execute_process(COMMAND ${Python_EXECUTABLE} ${ATTRIBUTES_PY} ${headers} ${projectt} ${CMAKE_CURRENT_BINARY_DIR}/attrsInclude COMMAND_ECHO STDOUT)
    set(attrsIncludeDir ${CMAKE_CURRENT_BINARY_DIR}/attrsInclude)
    target_include_directories(${projectt} PRIVATE ${attrsIncludeDir})
    target_sources(${projectt} PRIVATE ${attrsIncludeDir}/${projectt}Attributes.cpp)
endfunction()

add_library(PetrolEngine ${SOURCE_FILES} ${HEADER_FILES})
set_property(TARGET PetrolEngine PROPERTY CXX_STANDARD 17)
implement_attributes(PetrolEngine)
target_include_directories(PetrolEngine PRIVATE attrsIncludeDir)
if(MINGW)
    set( ALSOFT_BACKEND_PIPEWIRE OFF CACHE BOOL "GLFW lib only" FORCE )
    set( ALSOFT_REQUIRE_DSOUND ON CACHE BOOL "GLFW lib only" FORCE )
endif()

if( WIN32 AND NOT MINGW )
    target_compile_definitions(PetrolEngine PUBLIC __IS_WINDOWS__=1)
elseif( UNIX OR MINGW AND NOT APPLE )
    target_compile_definitions(PetrolEngine PUBLIC __IS_LINUX__=1)
elseif( APPLE )
    target_compile_definitions(PetrolEngine PUBLIC __IS_APPLE__=1)
endif()

#target_compile_features(PetrolEngine PUBLIC cxx_std_23)

link_libraries(PetrolEngine ${STATIC_LIBS})
set(STATIC_LIBS ${STATIC_LIBS} PARENT_SCOPE)

target_include_directories(PetrolEngine
    PUBLIC src
    PUBLIC ${INCLUDE_DIRS}
)

set(PETROL_ENGINE_INCLUDE ${INCLUDE_DIRS} PARENT_SCOPE)
execute_process(COMMAND cloc ${SOURCE_FILES} ${HEADER_FILES})
