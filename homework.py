from math import gcd
from collections import Counter
import arabic_reshaper
from bidi.algorithm import get_display

ARABIC_LETTERS = [
    'ا', 'ل', 'ن', 'م', 'ي', 'و', 'ر', 'ت', 'ب', 'ع',
    'ه', 'ف', 'ك', 'ق', 'ح', 'ج', 'ش', 'س', 'د', 'ث',
    'خ', 'ذ', 'ص', 'ز', 'ط', 'غ', 'ظ', 'ض'
]

ARABIC_FREQ = [
    12.73, 9.10, 7.13, 6.29, 5.88, 5.78, 5.61, 5.32, 4.64, 4.31,
     3.85, 3.30, 3.15, 2.96, 2.56, 2.29, 2.12, 1.90, 1.65, 1.53,
     1.42, 1.26, 1.15, 0.88, 0.68, 0.56, 0.36, 0.28
]

n_lettres = len(ARABIC_LETTERS)
lettre_index = {ch: i for i, ch in enumerate(ARABIC_LETTERS)}
ref_triee = [l for l, _ in sorted(zip(ARABIC_LETTERS, ARABIC_FREQ), key=lambda x: -x[1])]


# pour corriger l'affichage de l'arabe dans le terminal windows
def fix_arabic(text):
    reshaped_text = arabic_reshaper.reshape(text)
    return get_display(reshaped_text)

# fonction mathematique pour trouver l'inverse modulaire
def mod_inverse(a, m):
    for x in range(1, m):
        if (a * x) % m == 1:
            return x
    return None

def get_arabic_only(text):
    return ''.join(ch for ch in text if ch in lettre_index)

# compter les lettres et calculer le pourcentage
def letter_frequencies(text):
    arabic = get_arabic_only(text)
    total = len(arabic)
    if total == 0:
        return {}
    counts = Counter(arabic)
    return {ch: (cnt / total) * 100 for ch, cnt in counts.items()}

# calculer la distance entre notre texte et l'arabe normal
def score_text(text):
    freqs = letter_frequencies(text)
    score = 0.0
    for letter, ref_pct in zip(ARABIC_LETTERS, ARABIC_FREQ):
        diff = freqs.get(letter, 0.0) - ref_pct
        score -= diff ** 2
    return score

def print_frequency_table():
    print("\nTableau de frequences de la langue arabe :")
    for letter, freq in zip(ARABIC_LETTERS, ARABIC_FREQ):
        print(f"{fix_arabic(letter)} : {freq:.2f}%")

# les fonctions pour chiffrer (pour pouvoir tester apres)
def caesar_encrypt(text, k):
    result = []
    for ch in text:
        if ch in lettre_index:
            result.append(ARABIC_LETTERS[(lettre_index[ch] + k) % n_lettres])
        else:
            result.append(ch)
    return ''.join(result)

def affine_encrypt(text, a, b):
    if gcd(a, n_lettres) != 1:
        raise ValueError("a doit etre premier avec 28")
    result = []
    for ch in text:
        if ch in lettre_index:
            result.append(ARABIC_LETTERS[(a * lettre_index[ch] + b) % n_lettres])
        else:
            result.append(ch)
    return ''.join(result)

def substitution_encrypt(text, key):
    return ''.join(key.get(ch, ch) for ch in text)

# les fonctions de dechiffrement normal
def caesar_decrypt(text, k):
    return caesar_encrypt(text, -k)

def affine_decrypt(text, a, b):
    a_inv = mod_inverse(a, n_lettres)
    if a_inv is None:
        return text
    result = []
    for ch in text:
        if ch in lettre_index:
            result.append(ARABIC_LETTERS[(a_inv * (lettre_index[ch] - b)) % n_lettres])
        else:
            result.append(ch)
    return ''.join(result)

def substitution_decrypt(text, key):
    inv_key = {v: k for k, v in key.items()}
    return ''.join(inv_key.get(ch, ch) for ch in text)


# methode brute force pour casser cesar
def break_caesar(ciphertext):
    meilleur = {'shift': 0, 'score': float('-inf'), 'text': ''}
    
    for k in range(n_lettres):
        decrypted = caesar_decrypt(ciphertext, k)
        score_actuel = score_text(decrypted)
        
        # on garde le meilleur score
        if score_actuel > meilleur['score']:
            meilleur = {'shift': k, 'score': score_actuel, 'text': decrypted}

    print(f"\n[Cassage Cesar] Meilleur decalage : k = {meilleur['shift']}")
    print(f"Texte dechiffre : {fix_arabic(meilleur['text'])}")
    return meilleur

# tester toutes les combinaisons a et b possibles
def break_affine(ciphertext):
    # a doit etre premier avec 28
    a_candidates = [a for a in range(1, n_lettres) if gcd(a, n_lettres) == 1]
    meilleur = {'a': 1, 'b': 0, 'score': float('-inf'), 'text': ''}

    for a in a_candidates:
        for b in range(n_lettres):
            decrypted = affine_decrypt(ciphertext, a, b)
            score_actuel = score_text(decrypted)
            
            if score_actuel > meilleur['score']:
                meilleur = {'a': a, 'b': b, 'score': score_actuel, 'text': decrypted}

    print(f"\n[Cassage Affine] Meilleure cle : a = {meilleur['a']}, b = {meilleur['b']}")
    print(f"Texte dechiffre : {fix_arabic(meilleur['text'])}")
    return meilleur

# on map les lettres les plus frequentes du code avec l'alphabet arabe
def break_substitution(ciphertext):
    cipher_freqs = letter_frequencies(ciphertext)
    cipher_sorted = [l for l, _ in sorted(cipher_freqs.items(), key=lambda x: -x[1])]
    
    mapping = {}
    for cipher_letter, plain_letter in zip(cipher_sorted, ref_triee):
        mapping[cipher_letter] = plain_letter

    decrypted = substitution_decrypt(ciphertext, mapping)

    print("\n[Cassage Substitution]")
    print("Note : La substitution automatique necessite souvent des ajustements manuels car le texte est court.")
    print(f"Texte dechiffre : {fix_arabic(decrypted)}")
    return {'mapping': mapping, 'text': decrypted}


# fonction pour tester le tout
def tester_programme():
    # une phrase sur la fac pour le test
    plaintext = "تعتبر جامعة العلوم والتكنولوجيا هواري بومدين بباب الزوار من اكبر الجامعات في الجزائر ونحن ندرس فيها تخصص هندسة البرمجيات"
    
    print("Test du programme de cryptographie\n")
    print(f"Texte original : {fix_arabic(plaintext)}")
    
    print_frequency_table()
    
    # tester le cassage de cesar
    k = 7
    cipher_caesar = caesar_encrypt(plaintext, k)
    print(f"\nChiffre (Cesar k={k}) : {fix_arabic(cipher_caesar)}")
    break_caesar(cipher_caesar)
    
    # tester le cassage affine
    a, b = 5, 11
    cipher_affine = affine_encrypt(plaintext, a, b)
    print(f"\nChiffre (Affine a={a}, b={b}) : {fix_arabic(cipher_affine)}")
    break_affine(cipher_affine)
    
    # tester le cassage par substitution
    import random
    random.seed(42)
    shuffled = ARABIC_LETTERS[:]
    random.shuffle(shuffled)
    subst_key = dict(zip(ARABIC_LETTERS, shuffled))
    cipher_subst = substitution_encrypt(plaintext, subst_key)
    
    print(f"\nChiffre (Substitution) : {fix_arabic(cipher_subst)}")
    break_substitution(cipher_subst)


if __name__ == "__main__":
    tester_programme()