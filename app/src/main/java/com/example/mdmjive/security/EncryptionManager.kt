package com.example.mdmjive.security

data class DeviceIntegrityResult(
    val isRooted: Boolean,
    val isEmulator: Boolean,
    val hasUnknownSources: Boolean,
    val integrityScore: Int
)

class DeviceCertificationManager {
    fun validateDeviceIntegrity(): DeviceIntegrityResult {
        val isRooted = SecurityChecker.isDeviceRooted()
        val isEmulator = SecurityChecker.isRunningOnEmulator()
        val hasUnknownSources = SecurityChecker.hasUnknownSources()
        val integrityScore = calculateIntegrityScore(isRooted, isEmulator, hasUnknownSources)

        return DeviceIntegrityResult(
            isRooted = isRooted,
            isEmulator = isEmulator,
            hasUnknownSources = hasUnknownSources,
            integrityScore = integrityScore
        )
    }

    private fun calculateIntegrityScore(isRooted: Boolean, isEmulator: Boolean, hasUnknownSources: Boolean): Int {
        var score = 100

        if (isRooted) score -= 40
        if (isEmulator) score -= 30
        if (hasUnknownSources) score -= 20

        return score.coerceAtLeast(0) // Asegura que el puntaje no sea negativo
    }
}
