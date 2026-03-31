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

rootProject.name = "eApps"

fun prop(name: String, default: String = "true") =
    (extra.properties[name] as? String) ?: providers.gradleProperty(name).getOrElse(default)

// Core modules (always included)
include(":core:common")
include(":core:storage")
include(":core:network")
include(":core:platform")
include(":core:ui")

// Productivity apps
val includeProductivity = prop("eapps.apps.productivity").toBoolean()
if (includeProductivity) {
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
}

// Media apps
val includeMedia = prop("eapps.apps.media").toBoolean()
if (includeMedia) {
    include(":apps:emusic")
    include(":apps:evideo")
    include(":apps:egallery")
    include(":apps:eplay")
}

// Games
val includeGames = prop("eapps.apps.games").toBoolean()
if (includeGames) {
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
}

// Connectivity
val includeConnectivity = prop("eapps.apps.connectivity").toBoolean()
if (includeConnectivity) {
    include(":apps:essh")
    include(":apps:eserial")
    include(":apps:echat")
    include(":apps:etunnel")
    include(":apps:evpn")
}

// Security
val includeSecurity = prop("eapps.apps.security").toBoolean()
if (includeSecurity) {
    include(":apps:evirustower")
    include(":apps:evnc")
}

// Web
include(":apps:eweb")

// Suite launcher
include(":apps:suite")
