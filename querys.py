def vencimientos():
    return f"""
    SELECT 
        Patente, 
        Tipo,
        Descripcion, 
        FechaVencimiento, 
        DiasVencimiento, 
        CASE
                WHEN DiasVencimiento < 0 THEN 'Vencido'
                WHEN DiasVencimiento BETWEEN 0 AND 15 THEN 'Por vencer'
                WHEN DiasVencimiento > 15 THEN 'En fecha'
        END AS ClasVTO,
        TipoVencimiento,
        Operacion,
        'Pendiente' Estado
    FROM (
    SELECT
            MEMEQH.MEMEQH_CODIGO as Patente,
            MEMEQH.MEMEQH_DESCRP as Descripcion,
            CASE
                WHEN MEMEQH_DESCRP LIKE '%tractor%' THEN 'Tractor'
                WHEN MEMEQH_DESCRP LIKE '%semi%' THEN 'Cisterna'
                WHEN MEMEQH_DESCRP LIKE '%Auto%' OR MEMEQH_DESCRP LIKE '%Camionet%' THEN 'Automovil'
                ELSE 'Automovil'
            END AS Tipo,
            (ISNULL((
    CONVERT(FLOAT,DATEDIFF(DAY,
    ISNULL(
    MAX(CASE WHEN STMPDH_DESCRP LIKE 'Matafuego%' THEN EOMONTH(USR_MEMEQA_NFECHA) ELSE USR_MEMEQA_NFECHA END)
    ,GETDATE() )
    ,GETDATE() )) * (-1)
    ),0)
    ) AS DiasVencimiento,
            CONVERT(varchar,(MAX(CASE WHEN STMPDH_DESCRP LIKE 'Matafuego%' THEN EOMONTH(USR_MEMEQA_NFECHA) ELSE USR_MEMEQA_NFECHA END)),5) AS FechaVencimiento  ,
            (SELECT STMPDH_DESCRP FROM
    STMPDH
    WHERE
    STMPDH_TIPPRO= USR_MEMEQA_TIPPRO AND
    STMPDH_ARTCOD= USR_MEMEQA_ARTCOD) AS TipoVencimiento,
    USR_GRTOPE_DESCRP Operacion
    FROM
            MEMEQH
            INNER JOIN USR_MEMEQA ON (MEMEQH.MEMEQH_CODIGO = USR_MEMEQA.USR_MEMEQA_CODIGO AND  (USR_MEMEQA.USR_MEMEQA_TIPPRO = 'VTO   ') )
            LEFT OUTER JOIN STMPDH ON (USR_MEMEQA.USR_MEMEQA_TIPPRO = STMPDH.STMPDH_TIPPRO AND USR_MEMEQA.USR_MEMEQA_ARTCOD = STMPDH.STMPDH_ARTCOD)
            LEFT JOIN USR_GRTOPE ON USR_GRTOPE_CODIGO = USR_MEMEQH_OPE
            --LEFT JOIN USR_BASEOP ON USR_BASEOP_CODIGO = USR_MEMEQH_BASEOP

    WHERE	(USR_MEMEQA_TIPPRO= 'VTO')
        and USR_MEMEQH_BASEOP = 2
        and MEMEQH_DEBAJA = 'N'
        -- and USR_MEMEQA_NFECHA between cast('' as date) and dateadd(DAY, 15, cast('' as date))
        and USR_MEMEQA_ARTCOD NOT IN ('046000','055000','008000','006000','035000','004001','039000','047000','028000','061000','058008') -- Calibracion; Critico Sensor; INV; Sedronar; Semi Calibra, Seguro YPF, Cedula Verde; Tapas Superiores, Critico 7 y 9
        -- and MEMEQH_CODIGO NOT IN (patentes)
    GROUP BY 	(MEMEQH_CODIGO),
            MEMEQH.MEMEQH_CODIGO,
            MEMEQH.MEMEQH_DESCRP,
            STMPDH.STMPDH_DESCRP,
            USR_MEMEQA.USR_MEMEQA_TIPPRO,
            USR_MEMEQA.USR_MEMEQA_ARTCOD,
            MEMEQH.USR_MEMEQH_ATRCLI,
            MEMEQH.USR_MEMEQH_CLIENT,
            MEMEQH.USR_MEMEQH_BASEOP,
            USR_GRTOPE.USR_GRTOPE_DESCRP) AS T
    -- WHERE DiasVencimiento 
    ORDER BY 4;
    """
