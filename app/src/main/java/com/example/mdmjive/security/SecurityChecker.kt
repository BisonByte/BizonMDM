package com.example.mdmjive.security

import android.content.Context
import android.provider.Settings
import android.os.Build
import timber.log.Timber
import java.io.File

object SecurityChecker {

    /**
     * Verifica si el dispositivo está rooteado.
     */
    fun isDeviceRooted(): Boolean {
        val rooted = checkRootBinaries() || checkTestKeys() || checkSuExists()
        Timber.d("Rooted check result: $rooted")
        return rooted
    }

    /**
     * Verifica si la aplicación se está ejecutando en un emulador.
     */
    fun isRunningOnEmulator(): Boolean {
        val emulator = (Build.FINGERPRINT.startsWith("generic")
                || Build.FINGERPRINT.startsWith("unknown")
                || Build.MODEL.contains("google_sdk")
                || Build.MODEL.contains("Emulator")
                || Build.MANUFACTURER.contains("Genymotion")
                || Build.BRAND.startsWith("generic")
                || Build.HARDWARE.contains("goldfish")
                || Build.HARDWARE.contains("ranchu")
                || Build.PRODUCT.contains("sdk"))
        Timber.d("Emulator check result: $emulator")
        return emulator
    }

    /**
     * Verifica si el dispositivo está en modo "debuggable".
     */
    fun isDebuggable(): Boolean {
        val debuggable = Build.TYPE == "debug"
        Timber.d("Debuggable check result: $debuggable")
        return debuggable
    }

    /**
     * Verifica si existen binarios comúnmente utilizados en dispositivos rooteados.
     */
    private fun checkRootBinaries(): Boolean {
        val paths = arrayOf("/system/bin/", "/system/xbin/", "/sbin/", "/system/sd/xbin/")
        val binaries = arrayOf("su", "busybox")
        val rootFound = paths.flatMap { path ->
            binaries.map { binary -> File(path + binary).exists() }
        }.any { it }
        Timber.d("Root binaries check result: $rootFound")
        return rootFound
    }

    /**
     * Verifica si el dispositivo contiene "test-keys" en las tags del sistema.
     */
    private fun checkTestKeys(): Boolean {
        val buildTags = Build.TAGS
        val testKeys = buildTags != null && buildTags.contains("test-keys")
        Timber.d("Test keys check result: $testKeys")
        return testKeys
    }

    /**
     * Verifica si el comando `su` está disponible en el sistema.
     */
    private fun checkSuExists(): Boolean {
        var process: Process? = null
        return try {
            process = Runtime.getRuntime().exec(arrayOf("/system/xbin/which", "su"))
            val exitValue = process.waitFor()
            Timber.d("SU binary check exit value: $exitValue")
            exitValue == 0
        } catch (e: Exception) {
            Timber.e("Error checking SU binary: ${e.message}")
            false
        } finally {
            process?.destroy()
        }
    }

    /**
     * Verifica si está habilitada la opción de instalar aplicaciones desde fuentes desconocidas.
     */
    fun hasUnknownSources(context: Context): Boolean {
        return try {
            val unknownSourcesAllowed = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                Settings.Secure.getInt(context.contentResolver, Settings.Secure.INSTALL_NON_MARKET_APPS) == 1
            } else {
                @Suppress("DEPRECATION")
                Settings.Secure.getInt(context.contentResolver, Settings.Secure.INSTALL_NON_MARKET_APPS) == 1
            }
            Timber.d("Unknown sources check result: $unknownSourcesAllowed")
            unknownSourcesAllowed
        } catch (e: Exception) {
            Timber.e("Error checking unknown sources: ${e.message}")
            false
        }
    }
}
