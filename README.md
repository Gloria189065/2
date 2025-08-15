# 密码学安全套件

![Python](https://img.shields.io/badge/python-3.8+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

整合SM4/SM2/数字水印/Google密码检查协议的完整实现

---

## 目录
1. [SM4加密优化](#sm4加密优化)  
2. [数字水印算法](#数字水印算法)  
3. [SM2签名协议](#sm2签名协议)  
4. [Google密码检查](#google密码检查协议)  

---

## SM4加密优化
### 算法核心
**轮函数**：\
F(X_i, X_{i+1}, X_{i+2}, X_{i+3}, rk_i) = X_i ⊕ T(X_{i+1} ⊕ X_{i+2} ⊕ X_{i+3} ⊕ rk_i)

**T变换**：\
T(·) = L(τ(·))\
τ(A) = (Sbox(a₀), Sbox(a₁), Sbox(a₂), Sbox(a₃))\
L(B) = B ⊕ (B <<< 2) ⊕ (B <<< 10) ⊕ (B <<< 18) ⊕ (B <<< 24)

### 优化技术
| 技术 | 加速比 | 实现方式 |
|------|--------|----------|
| T-table | 3.2x | 预计算S盒与线性变换组合 |
| AESNI | 7.1x | 使用`_mm_aesenc_si128`指令 |
| GFNI | 9.3x | 伽罗瓦域新指令加速 |

---

## 数字水印算法
### DWT-SIFT混合算法
1. **频域嵌入**：\
LL₃ʷᵐ = LL₃ + α · W · mask\
   其中α为强度因子，mask为SIFT特征区域

2. **特征点检测**：\
D(x,y,σ) = [G(x,y,kσ) - G(x,y,σ)] * I(x,y)


### 鲁棒性测试
| 攻击类型 | PSNR(dB) | NCC |
|----------|----------|-----|
| 旋转30° | 38.2 | 0.91 |
| 裁剪20% | 42.1 | 0.86 |
| JPEG压缩(Q=70) | 45.7 | 0.94 |

---

## SM2签名协议
### 数学基础
**椭圆曲线参数**：\
E: y² ≡ x³ + ax + b (mod p)\
p = 2²⁵⁶ - 2²²⁴ + 2¹⁹² + 2⁹⁶ - 1


**签名生成**：\
e = H(Z_A || M)\
k ∈ [1, n-1]\
(x₁, y₁) = k·G\
r = (e + x₁) mod n\
s = (1 + d_A)⁻¹ · (k - r·d_A) mod n\

### 安全漏洞
**随机数重用攻击**：

已知k重复时：\
d_A ≡ (s₂ - s₁) / (r₁ - r₂ + s₁ - s₂) mod n

## Google密码检查协议
### 协议流程
```mermaid
sequenceDiagram
    Client->>Server: h=Hash(pwd), Blind(h)
    Server-->>Client: {s: salt, B=Blind(h+s)}
    Client->>Server: Open(B)
    Server->>DB: Check h+s in breach DB
