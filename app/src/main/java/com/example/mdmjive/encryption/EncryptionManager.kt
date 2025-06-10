import android.content.Context
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import java.security.SecureRandom
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey
import javax.crypto.spec.GCMParameterSpec
import android.util.Base64

class EncryptionManager(private val context: Context) {

    private val keyStore: KeyStore = KeyStore.getInstance("AndroidKeyStore").apply {
        load(null)
    }

    private val keyAlias = "EncryptionKeyAlias"
    private val transformation = "AES/GCM/NoPadding"
    private val ivLength = 12 // Longitud recomendada para GCM

    init {
        if (!keyStore.containsAlias(keyAlias)) {
            generateKey()
        }
    }

    /**
     * Cifra datos utilizando AES/GCM y devuelve el resultado en Base64.
     */
    fun encryptData(data: String): String {
        val cipher = Cipher.getInstance(transformation)
        cipher.init(Cipher.ENCRYPT_MODE, getSecretKey())
        val iv = cipher.iv // IV generado automáticamente
        val encryptedData = cipher.doFinal(data.toByteArray(Charsets.UTF_8))
        val combined = iv + encryptedData // Combina IV y datos cifrados
        return Base64.encodeToString(combined, Base64.DEFAULT)
    }

    /**
     * Descifra datos previamente cifrados y devueltos en Base64.
     */
    fun decryptData(encryptedData: String): String {
        val combined = Base64.decode(encryptedData, Base64.DEFAULT)
        val iv = combined.sliceArray(0 until ivLength)
        val encryptedBytes = combined.sliceArray(ivLength until combined.size)

        val cipher = Cipher.getInstance(transformation)
        cipher.init(Cipher.DECRYPT_MODE, getSecretKey(), GCMParameterSpec(128, iv))
        val decryptedData = cipher.doFinal(encryptedBytes)
        return String(decryptedData, Charsets.UTF_8)
    }

    /**
     * Genera una clave AES/GCM en AndroidKeyStore.
     */
    private fun generateKey() {
        val keyGenerator = KeyGenerator.getInstance(KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")
        val keySpec = KeyGenParameterSpec.Builder(
            keyAlias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        ).setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setKeySize(256) // Tamaño de clave AES de 256 bits
            .build()
        keyGenerator.init(keySpec)
        keyGenerator.generateKey()
    }

    /**
     * Obtiene la clave AES desde AndroidKeyStore.
     */
    private fun getSecretKey(): SecretKey {
        return keyStore.getKey(keyAlias, null) as SecretKey
    }
}
