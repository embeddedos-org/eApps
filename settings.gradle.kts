pluginManagement {
    includeBuild("build-logic")
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "eAppSuite"

// Core modules
include(":core:common")
include(":core:storage")
include(":core:network")
include(":core:platform")
include(":core:ui")

// Productivity apps
include(":apps:ecal")
include(":apps:enote")
include(":apps:eftp")
include(":apps:econverter")
include(":apps:etools")
include(":apps:ebuffer")
include(":apps:ecleaner")
include(":apps:eclock")
include(":apps:efiles")
include(":apps:ezip")
include(":apps:epaint")
include(":apps:epdf")
include(":apps:eguard")

// Media apps
include(":apps:emusic")
include(":apps:evideo")
include(":apps:egallery")
include(":apps:eplay")

// Games
include(":apps:snake")
include(":apps:tetris")
include(":apps:minesweeper")
include(":apps:dice")
include(":apps:echess")
include(":apps:ebirds")
include(":apps:eslice")
include(":apps:erunner")
include(":apps:eblocks")
include(":apps:ecrush")
include(":apps:esurfer")

// Connectivity
include(":apps:essh")
include(":apps:eserial")
include(":apps:echat")
include(":apps:etunnel")
include(":apps:evpn")

// Security
include(":apps:evirustower")
include(":apps:evnc")

// Web
include(":apps:eweb")

// Suite launcher
include(":apps:suite")
pluginManagement {
    includeBuild("build-logic")
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositories {
        google()
        mavenCentral()
    }
}

rootProject.name = "eAppSuite"

// Core shared libraries
include(":core:common")
include(":core:ui")
include(":core:storage")
include(":core:network")
include(":core:platform")

// Apps — Productivity
include(":apps:ecal")
include(":apps:enote")
include(":apps:eftp")
include(":apps:econverter")
include(":apps:etools")
include(":apps:ebuffer")
include(":apps:ecleaner")
include(":apps:eclock")
include(":apps:efiles")
include(":apps:ezip")
include(":apps:epaint")
include(":apps:epdf")
include(":apps:eguard")

// Apps — Media
include(":apps:emusic")
include(":apps:evideo")
include(":apps:egallery")
include(":apps:eplay")

// Apps — Games
include(":apps:snake")
include(":apps:tetris")
include(":apps:minesweeper")
include(":apps:dice")
include(":apps:echess")
include(":apps:ebirds")
include(":apps:eslice")
include(":apps:erunner")
include(":apps:eblocks")
include(":apps:ecrush")
include(":apps:esurfer")

// Apps — Connectivity
include(":apps:essh")
include(":apps:eserial")
include(":apps:echat")
include(":apps:etunnel")
include(":apps:evpn")

// Apps — Security
include(":apps:evirustower")
include(":apps:evnc")

// Apps — Web
include(":apps:eweb")

// Apps — Suite Launcher
include(":apps:suite")
