DONATION_QUERY = """

    SELECT
        sigla_loja,
        codbar,
        codtotvs,
        produto,
        categoria_modular,
        ROUND(valor_perda, 2) as valor_perda,
        quantidade,
        data_perda
    FROM
        dw_doacao

"""