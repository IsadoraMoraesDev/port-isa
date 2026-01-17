valor_produto = float(input("digite o valor do produto"))
valor_pago = float(input("digite o valor pago"))
troco = valor_pago - valor_produto
print(troco)
if troco < 0:
    print(f"falta R$ {abs(troco):.2f}para pagar o produto")
else:
    print(f"seu troco é R$ {troco:.2f}.Obrigado pela compra") 