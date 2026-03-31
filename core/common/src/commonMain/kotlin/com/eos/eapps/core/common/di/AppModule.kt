package com.eos.eapps.core.common.di

import com.eos.eapps.core.common.constants.AppRegistry

object AppModule {
    val registry = AppRegistry

    fun allApps() = registry.apps
    fun appById(id: String) = registry.getApp(id)
    fun appsByCategory(category: com.eos.eapps.core.common.models.AppCategory) =
        registry.getAppsInCategory(category)
    fun searchApps(query: String) = registry.search(query)
}
