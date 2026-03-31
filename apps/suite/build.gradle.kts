plugins {
    id("compose-app-convention")
}

android {
    namespace = "com.eos.eappsuite.suite"
    defaultConfig {
        applicationId = "com.eos.eappsuite.suite"
        versionCode = 1
        versionName = "1.0.0"
    }
}

compose.desktop {
    application {
        mainClass = "com.eos.eappsuite.suite.MainKt"
    }
}

kotlin {
    sourceSets {
        commonMain.dependencies {
            implementation(project(":core:common"))
            implementation(project(":core:ui"))
            implementation(project(":core:storage"))
            implementation(project(":core:network"))
            implementation(project(":core:platform"))

            // All apps embedded in the suite launcher
            implementation(project(":apps:ecal"))
            implementation(project(":apps:enote"))
            implementation(project(":apps:eftp"))
            implementation(project(":apps:econverter"))
            implementation(project(":apps:etools"))
            implementation(project(":apps:ebuffer"))
            implementation(project(":apps:ecleaner"))
            implementation(project(":apps:eclock"))
            implementation(project(":apps:efiles"))
            implementation(project(":apps:ezip"))
            implementation(project(":apps:epaint"))
            implementation(project(":apps:epdf"))
            implementation(project(":apps:eguard"))
            implementation(project(":apps:emusic"))
            implementation(project(":apps:evideo"))
            implementation(project(":apps:egallery"))
            implementation(project(":apps:eplay"))
            implementation(project(":apps:snake"))
            implementation(project(":apps:tetris"))
            implementation(project(":apps:minesweeper"))
            implementation(project(":apps:dice"))
            implementation(project(":apps:echess"))
            implementation(project(":apps:ebirds"))
            implementation(project(":apps:eslice"))
            implementation(project(":apps:erunner"))
            implementation(project(":apps:eblocks"))
            implementation(project(":apps:ecrush"))
            implementation(project(":apps:esurfer"))
            implementation(project(":apps:essh"))
            implementation(project(":apps:eserial"))
            implementation(project(":apps:echat"))
            implementation(project(":apps:etunnel"))
            implementation(project(":apps:evpn"))
            implementation(project(":apps:evirustower"))
            implementation(project(":apps:evnc"))
            implementation(project(":apps:eweb"))
        }
    }
}
