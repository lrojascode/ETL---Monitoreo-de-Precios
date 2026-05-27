package com.pricemonitor.backend.dto;

import jakarta.validation.constraints.Min;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.Getter;
import lombok.Setter;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;

@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
public class ProductDto {

    @NotBlank(message = "El SKU del supermercado no puede estar vacío")
    private String skuSupermarket;

    @NotBlank(message = "El nombre del producto no puede estar vacío")
    private String name;

    @NotBlank(message = "La marca no puede estar vacía")
    private String brand;

    @NotBlank(message = "La categoría no puede estar vacía")
    private String category;

    @NotNull(message = "El precio normal no puede ser nulo")
    @Min(value = 0, message = "El precio normal debe ser mayor o igual a 0")
    private Integer priceNormal;

    private Integer pricePromo;

    @NotBlank(message = "La URL del producto no puede estar vacía")
    private String url;

    private Boolean isAvailable = true;
}
